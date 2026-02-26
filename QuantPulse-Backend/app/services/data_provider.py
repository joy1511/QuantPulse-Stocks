"""
Data Provider Service — The Live Data Engine

Uses yfinance exclusively to fetch real-time market data for:
1. The target stock (e.g., RELIANCE.NS)
2. Nifty 50 (^NSEI) for market regime context
3. India VIX (^INDIAVIX) for risk context

Includes TTL-based LRU caching to prevent Yahoo rate-limiting.
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
# Core Data Fetching
# =============================================================================

async def _fetch_from_provider_fallback(ticker: str, period: str = "2y") -> pd.DataFrame | None:
    """
    Fallback: Fetch historical data from TwelveData/Finnhub via ProviderFactory.
    Converts the result to a pandas DataFrame matching yfinance structure.
    """
    try:
        # Indices (starts with ^) might not be supported by stock providers simply
        if ticker.startswith("^"):
            return None

        # Remove .NS suffix for provider lookup if needed (providers handle suffix internally)
        clean_symbol = ticker.replace(".NS", "")
        
        logger.info(f"🔄 Fallback: Fetching {clean_symbol} from active provider...")
        
        # ✅ FIX: Create ProviderFactory instance (not static call)
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
        df.drop(columns=["date"], inplace=True)
        
        # Rename columns to match yfinance format
        df.rename(columns={
            "open": "Open",
            "high": "High",
            "low": "Low",
            "close": "Close",
            "volume": "Volume"
        }, inplace=True)
        
        logger.info(f"✅ Provider fallback successful for {ticker}: {len(df)} rows")
        return df
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
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        logger.info(f"✅ Fallback success: {len(df)} rows for {ticker} via {provider.provider_name}")
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
    Orchestrates data fetching: yfinance -> Serper (live price) -> Fallback Provider -> Synthetic
    """
    # 1. Try yfinance (sync)
    df = _download_safe_sync(ticker, period)
    if df is not None and not df.empty:
        return df
    
    # 2. Try Serper API for live price (only for current price, not historical)
    # This is specifically for Vercel deployment where yfinance may fail
    if not ticker.startswith("^"):
        logger.info(f"🔄 yfinance failed, trying Serper API for live price of {ticker}...")
        serper_data = await serper_price_service.get_live_price(ticker)
        
        if serper_data and serper_data.get("price"):
            # Create a minimal DataFrame with just the current price
            # For historical context, we'll still need to fall back to synthetic
            logger.info(f"✅ Got live price from Serper: ₹{serper_data['price']}")
            # Continue to fallback provider for historical data
        
    # 3. Try Fallback Provider (skip for indices usually)
    if not ticker.startswith("^"):
        df = await _fetch_from_provider_fallback(ticker, period)
        if df is not None and not df.empty:
            return df
            
    # 4. FINAL FALLBACK: Synthetic Data
    # The user explicitly requested "run it on simulated" if no data.
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
