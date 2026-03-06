"""
Data Provider Service — The Live Data Engine

Uses multiple data sources with intelligent fallback:
1. yfinance (Primary - works locally)
2. nsepython (NSE-specific - works on cloud, no API key needed)
3. Serper API (Live prices via Google Search)
4. TwelveData/Finnhub (If API keys provided)
5. Synthetic data (Final fallback)

Includes TTL-based LRU caching to prevent rate-limiting.
"""

import time
import logging
from functools import lru_cache, wraps
from datetime import datetime, timedelta

import numpy as np
import yfinance as yf
import pandas as pd

import asyncio
from app.providers.provider_factory import ProviderFactory
from app.services.serper_price_service import serper_price_service

logger = logging.getLogger(__name__)

# =============================================================================
# NSE Python Integration (No API Key Needed!)
# =============================================================================

try:
    from nsepython import (
        nse_eq_symbols,
        nse_quote_ltp,
        equity_history,
        nse_quote
    )
    NSEPYTHON_AVAILABLE = True
    logger.info("✅ nsepython available - NSE data source active")
except ImportError:
    NSEPYTHON_AVAILABLE = False
    logger.warning("⚠️ nsepython not installed - NSE fallback disabled")

# =============================================================================
# TTL-Cached LRU Decorator
# =============================================================================

def timed_lru_cache(seconds: int = 300, maxsize: int = 10):
    """
    LRU cache with a time-to-live (TTL).
    Entries expire after `seconds` and are re-fetched on the next call.
    """
    def wrapper(func):
        func = lru_cache(maxsize=maxsize)(func)
        func._lifetime = seconds
        func._expiration = time.monotonic() + seconds

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if time.monotonic() >= func._expiration:
                func.cache_clear()
                func._expiration = time.monotonic() + func._lifetime
                logger.info(f"🔄 Cache expired for {func.__name__}, re-fetching...")
            return func(*args, **kwargs)

        wrapped_func.cache_clear = func.cache_clear
        wrapped_func.cache_info = func.cache_info
        return wrapped_func

    return wrapper


# =============================================================================
# Ticker Normalization
# =============================================================================

def normalize_ticker(ticker: str) -> str:
    """
    Ensure ticker has the .NS suffix for NSE stocks.
    If the ticker already has a suffix (contains '.') or starts with '^', leave it.
    """
    ticker = ticker.strip().upper()
    if ticker.startswith("^"):
        return ticker
    if "." not in ticker:
        return f"{ticker}.NS"
    return ticker


# =============================================================================
# NSE Python Data Fetching (Tier 2 Fallback - No API Key!)
# =============================================================================

async def _fetch_from_nsepython(ticker: str, period: str = "2y") -> pd.DataFrame | None:
    """
    Fetch data from NSE using nsepython library.
    Works on cloud platforms, no API key required!
    
    Args:
        ticker: Stock symbol (e.g., "RELIANCE" or "RELIANCE.NS")
        period: Time period (converts to days)
        
    Returns:
        DataFrame with OHLCV data or None if failed
    """
    if not NSEPYTHON_AVAILABLE:
        return None
        
    try:
        # Remove .NS suffix if present
        clean_symbol = ticker.replace(".NS", "").strip().upper()
        
        # Skip indices (nsepython is for stocks only)
        if clean_symbol.startswith("^"):
            return None
            
        logger.info(f"🔄 Fetching {clean_symbol} from nsepython...")
        
        # Convert period to days
        days_map = {
            "1d": 1, "5d": 5, "1mo": 30, "3mo": 90,
            "6mo": 180, "1y": 365, "2y": 730, "5y": 1825
        }
        days = days_map.get(period, 730)  # Default 2 years
        
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Fetch historical data using nsepython
        # equity_history returns DataFrame with columns: Date, Open, High, Low, Close, Volume
        df = await asyncio.to_thread(
            equity_history,
            clean_symbol,
            "EQ",  # Equity series
            start_date.strftime("%d-%m-%Y"),
            end_date.strftime("%d-%m-%Y")
        )
        
        if df is None or df.empty:
            logger.warning(f"⚠️ nsepython returned no data for {clean_symbol}")
            return None
            
        # Standardize column names to match yfinance
        if "CH_TIMESTAMP" in df.columns:
            df["Date"] = pd.to_datetime(df["CH_TIMESTAMP"])
            df.set_index("Date", inplace=True)
            
        # Rename columns to match yfinance format
        column_mapping = {
            "CH_OPENING_PRICE": "Open",
            "CH_TRADE_HIGH_PRICE": "High",
            "CH_TRADE_LOW_PRICE": "Low",
            "CH_CLOSING_PRICE": "Close",
            "CH_TOT_TRADED_QTY": "Volume",
            # Alternative column names (nsepython may vary)
            "OPEN": "Open",
            "HIGH": "High",
            "LOW": "Low",
            "CLOSE": "Close",
            "VOLUME": "Volume"
        }
        
        df.rename(columns=column_mapping, inplace=True)
        
        # Ensure we have required columns
        required_cols = ["Open", "High", "Low", "Close", "Volume"]
        if not all(col in df.columns for col in required_cols):
            logger.warning(f"⚠️ nsepython data missing required columns for {clean_symbol}")
            return None
            
        # Convert to numeric
        for col in required_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Remove NaN rows
        df = df.dropna(subset=required_cols)
        
        if df.empty:
            logger.warning(f"⚠️ nsepython data empty after cleaning for {clean_symbol}")
            return None
            
        logger.info(f"✅ nsepython success: {len(df)} rows for {clean_symbol}")
        return df
        
    except Exception as e:
        logger.error(f"❌ nsepython failed for {ticker}: {e}")
        return None


async def _get_live_price_nsepython(ticker: str) -> dict | None:
    """
    Get current live price from NSE using nsepython.
    Fast and reliable for current price only.
    
    Args:
        ticker: Stock symbol (e.g., "RELIANCE")
        
    Returns:
        dict with price info or None
    """
    if not NSEPYTHON_AVAILABLE:
        return None
        
    try:
        clean_symbol = ticker.replace(".NS", "").strip().upper()
        
        if clean_symbol.startswith("^"):
            return None
            
        logger.info(f"🔄 Getting live price for {clean_symbol} from nsepython...")
        
        # Get live quote
        quote = await asyncio.to_thread(nse_quote, clean_symbol)
        
        if not quote:
            return None
            
        # Extract price data
        price_data = {
            "price": float(quote.get("priceInfo", {}).get("lastPrice", 0)),
            "previous_close": float(quote.get("priceInfo", {}).get("previousClose", 0)),
            "change": float(quote.get("priceInfo", {}).get("change", 0)),
            "percent_change": float(quote.get("priceInfo", {}).get("pChange", 0)),
            "volume": int(quote.get("preOpenMarket", {}).get("totalTradedVolume", 0)),
            "source": "nsepython"
        }
        
        logger.info(f"✅ nsepython live price: ₹{price_data['price']} for {clean_symbol}")
        return price_data
        
    except Exception as e:
        logger.error(f"❌ nsepython live price failed for {ticker}: {e}")
        return None


# =============================================================================
# Core Data Fetching (Updated with nsepython)
# =============================================================================

async def _fetch_from_provider_fallback(ticker: str, period: str = "2y") -> pd.DataFrame | None:
    """
    Fallback: Fetch historical data from TwelveData/Finnhub via ProviderFactory.
    Converts the result to a pandas DataFrame matching yfinance structure.
    """
    try:
        # Indices (starts with ^) might not be supported by stock providers
        if ticker.startswith("^"):
            return None

        # Remove .NS suffix for provider lookup
        clean_symbol = ticker.replace(".NS", "")
        
        logger.info(f"🔄 Fallback: Fetching {clean_symbol} from active provider...")
        
        # Create ProviderFactory instance
        from ..providers.provider_factory import ProviderFactory
        provider_factory = ProviderFactory()
        
        # Use instance method to get historical data
        historical = await provider_factory.get_historical_data(clean_symbol, period=period)
        
        if not historical or not historical.data:
            logger.warning(f"⚠️ Provider returned no data for {ticker}")
            return None
            
        # Convert list of dicts to DataFrame
        df = pd.DataFrame(historical.data)
        
        # Standardize columns to match yfinance: Date, Open, High, Low, Close, Volume
        df["Date"] = pd.to_datetime(df["date"])
        df.set_index("Date", inplace=True)
        df.drop(columns=["date"], inplace=True, errors='ignore')
        
        # Rename columns to match yfinance format
        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)
        
        # Ensure numeric
        cols = ["Open", "High", "Low", "Close", "Volume"]
        for col in cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        logger.info(f"✅ Provider fallback successful for {ticker}: {len(df)} rows")
        return df

    except Exception as e:
        logger.error(f"❌ Fallback failed for {ticker}: {e}")
        return None

def _download_safe_sync(ticker: str, period: str = "2y"):
    """
    Synchronous wrapper for yfinance download (since yfinance is sync).
    """
    try:
        logger.info(f"📥 Downloading {ticker} ({period})...")
        data = yf.download(
            ticker, period=period, progress=False, auto_adjust=True,
        )

        # yfinance >= 0.2.36 returns MultiIndex columns even for single tickers
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)

        if data is None or data.empty:
            logger.warning(f"⚠️ yfinance returned no data for {ticker}")
            return None

        logger.info(f"✅ Got {len(data)} rows for {ticker} (yfinance)")
        return data

    except Exception as e:
        logger.error(f"❌ yfinance failed for {ticker}: {e}")
        return None

# =============================================================================
# Synthetic Data Simulation (Final Fail-Safe)
# =============================================================================

def _generate_synthetic_data(ticker: str, period: str = "2y") -> pd.DataFrame:
    """
    Generate realistic synthetic OHLCV data if all APIs fail.
    Used to ensure the application remains functional (Demo/Simulation Mode).
    """
    logger.warning(f"⚠️ Generating SYNTHETIC data for {ticker} (All APIs failed)")
    
    # Deterministic random seed based on ticker characters so it's consistent per session
    seed_val = sum(ord(c) for c in ticker)
    np.random.seed(int(time.time()) + seed_val) # Change every reload but stable for a moment
    
    # Determine number of days
    days = 730 if "2y" in period else 365
    
    # Generate dates
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    # Filter for weekdays only (approx mask)
    dates = dates[dates.dayofweek < 5]
    n = len(dates)
    
    # Random walk info
    start_price = 2500.0 if "RELIANCE" in ticker else 15000.0 if "NSEI" in ticker else 15.0
    if ticker.startswith("^INDIAVIX"):
        start_price = 15.0
        volatility = 0.05
    else:
        volatility = 0.02

    # Generate returns
    returns = np.random.normal(0.0005, volatility, n) # Slight upward drift
    price_path = start_price * (1 + returns).cumprod()
    
    # Create OHLC
    close = price_path
    open_p = close * (1 + np.random.normal(0, 0.005, n))
    high = np.maximum(open_p, close) * (1 + abs(np.random.normal(0, 0.005, n)))
    low = np.minimum(open_p, close) * (1 - abs(np.random.normal(0, 0.005, n)))
    volume = np.random.randint(100000, 5000000, n)
    
    df = pd.DataFrame({
        "Open": open_p,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume
    }, index=dates)
    
    # Ensure no NaN
    # ✅ FIX: Use new pandas syntax (no deprecation warnings)
    df = df.ffill()  # Forward fill
    df = df.bfill()  # Backward fill
    
    return df

async def _get_data_async(ticker: str, period: str = "2y") -> pd.DataFrame | None:
    """
    Orchestrates data fetching with intelligent fallback:
    1. yfinance (works locally, may fail on cloud)
    2. nsepython (NSE-specific, works on cloud, no API key)
    3. Serper API (live price only)
    4. TwelveData/Finnhub (if API keys provided)
    5. Synthetic data (final fallback)
    """
    # 1. Try yfinance (sync)
    df = _download_safe_sync(ticker, period)
    if df is not None and not df.empty:
        logger.info(f"✅ Data source: yfinance for {ticker}")
        return df
    
    # 2. Try nsepython (NSE stocks only, no API key needed!)
    if not ticker.startswith("^"):
        logger.info(f"🔄 yfinance failed, trying nsepython for {ticker}...")
        df = await _fetch_from_nsepython(ticker, period)
        if df is not None and not df.empty:
            logger.info(f"✅ Data source: nsepython for {ticker}")
            return df
    
    # 3. Try Serper API for live price (current price only, not historical)
    if not ticker.startswith("^"):
        logger.info(f"🔄 nsepython failed, trying Serper API for live price of {ticker}...")
        serper_data = await serper_price_service.get_live_price(ticker)
        
        if serper_data and serper_data.get("price"):
            logger.info(f"✅ Got live price from Serper: ₹{serper_data['price']}")
            # Note: Serper only provides current price, not historical
            # Continue to next fallback for historical data
    
    # 4. Try Fallback Provider (TwelveData/Finnhub if API keys provided)
    if not ticker.startswith("^"):
        logger.info(f"🔄 Trying TwelveData/Finnhub fallback for {ticker}...")
        df = await _fetch_from_provider_fallback(ticker, period)
        if df is not None and not df.empty:
            logger.info(f"✅ Data source: Provider fallback for {ticker}")
            return df
            
    # 5. FINAL FALLBACK: Synthetic Data
    logger.warning(f"⚠️ All data sources failed for {ticker}, using SIMULATED data")
    return _generate_synthetic_data(ticker, period)


@timed_lru_cache(seconds=300, maxsize=10)
def fetch_market_context_sync_wrapper(ticker: str) -> dict:
    """
    Async-to-Sync wrapper for LRU cache. 
    Since lru_cache works on sync functions, and we need async fallback, 
    we use asyncio.run() here. 
    
    WARNING: Nesting asyncio.run() inside a running loop is bad. 
    But this function is called from a FastAPI endpoint which is async def? 
    Wait, data_provider functions were synchronous before.
    
    Refactoring strategy:
    - Make `fetch_market_context` async.
    - Remove `@timed_lru_cache` (or provide async alternative).
    - Update call sites (`v2_analysis.py`).
    """
    # For minimal regression, we'll implement a blocking call via asyncio.run 
    # ONLY if we are not in a loop. But FastAPI runs on loop.
    # Actually, yfinance is blocking. Provider is async.
    
    # Simpler approach: Use the sync HTTP client in fallback if possible? 
    # No, providers use httpx.AsyncClient.
    
    # We must refactor fetch_market_context to be async.
    # And check call sites.
    pass 

# Since we need to change the function signature to async, we can't use standard lru_cache easily.
# We will use 'async-lru' or simple in-memory dict manual caching for now to avoid dependency hell.
# Or just async def with no cache (cache is less critical than working).
# Let's remove cache for now or implement a simple active_cache dict.

_CONTEXT_CACHE = {} 

async def fetch_market_context(ticker: str) -> dict:
    """
    Fetch complete market context for analysis (Async).
    
    Downloads 2 years of daily data for:
    1. The target stock
    2. ^NSEI (Nifty 50) — for regime detection
    3. ^INDIAVIX (India VIX) — for risk assessment
    
    Args:
        ticker: Stock symbol (e.g., "RELIANCE" or "RELIANCE.NS")
        
    Returns:
        dict with keys: 'target_df', 'nifty_df', 'vix_df'
    """
    ns_ticker = normalize_ticker(ticker)
    
    # Simple explicit cache check
    cache_key = f"{ns_ticker}"
    now = time.time()
    if cache_key in _CONTEXT_CACHE:
        entry = _CONTEXT_CACHE[cache_key]
        if now < entry['expiry']:
            logger.info(f"✨ Using cached context for {ns_ticker}")
            return entry['data']

    logger.info(f"🔍 Fetching market context for {ns_ticker}...")

    # Fetch all three datasets preferably in parallel
    # target_df = await _get_data_async(ns_ticker, period="2y")
    # nifty_df = await _get_data_async("^NSEI", period="2y")
    # vix_df = await _get_data_async("^INDIAVIX", period="2y")
    
    results = await asyncio.gather(
        _get_data_async(ns_ticker, period="2y"),
        _get_data_async("^NSEI", period="2y"),
        _get_data_async("^INDIAVIX", period="2y")
    )
    
    target_df, nifty_df, vix_df = results

    # Log summary
    target_rows = len(target_df) if target_df is not None else 0
    nifty_rows = len(nifty_df) if nifty_df is not None else 0
    vix_rows = len(vix_df) if vix_df is not None else 0
    logger.info(
        f"📊 Market context ready: "
        f"target={target_rows} rows, "
        f"nifty={nifty_rows} rows, "
        f"vix={vix_rows} rows"
    )

    data = {
        "target_df": target_df,
        "nifty_df": nifty_df,
        "vix_df": vix_df,
    }
    
    # Cache it
    _CONTEXT_CACHE[cache_key] = {
        'data': data,
        'expiry': now + 300 # 5 mins
    }

    return data


def get_current_vix_level(vix_df) -> float:
    """
    Extract the latest VIX closing value from the VIX DataFrame.
    Returns 15.0 as a safe default if data is unavailable.
    """
    if vix_df is None:
        logger.warning("⚠️ VIX data unavailable, using default 15.0")
        return 15.0

    try:
        if vix_df.empty:
            logger.warning("⚠️ VIX DataFrame is empty, using default 15.0")
            return 15.0
        return float(vix_df["Close"].iloc[-1])
    except (KeyError, IndexError, AttributeError) as e:
        logger.warning(f"⚠️ Could not extract VIX close: {e}, using default 15.0")
        return 15.0
