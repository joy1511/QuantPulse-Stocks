"""
Finnhub Provider

Fallback stock data provider using Finnhub API.
Activated when primary provider (Twelve Data) fails.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import time

from .base import BaseStockProvider, StockQuote, CompanyProfile, HistoricalData

logger = logging.getLogger(__name__)


class FinnhubProvider(BaseStockProvider):
    """
    Finnhub API provider for stock market data.
    
    Features:
    - Real-time quotes
    - Historical data
    - Company profiles
    - Fallback provider with different API structure
    """
    
    BASE_URL = "https://finnhub.io/api/v1"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 8):
        super().__init__(api_key, timeout)
        self.provider_name = "Finnhub"
    
    async def get_stock_quote(self, symbol: str) -> StockQuote:
        """
        Fetch real-time stock quote from Finnhub.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            
        Returns:
            StockQuote: Normalized quote data
        """
        # Finnhub uses different symbol format for NSE
        finnhub_symbol = f"{self._convert_to_nse_symbol(symbol)}.NS"
        
        params = {
            "symbol": finnhub_symbol,
            "token": self.api_key or "demo"
        }
        
        url = f"{self.BASE_URL}/quote"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First attempt
                response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    # Retry once
                    logger.warning(f"Finnhub first attempt failed: {response.status_code}")
                    response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                
                data = response.json()
                
                # Check for API error or empty response
                if not data or data.get("c") is None:
                    raise Exception("No data available")
                
                return self._normalize_quote(data, symbol)
                
        except httpx.TimeoutException:
            logger.error(f"Finnhub timeout for symbol: {symbol}")
            raise Exception("Request timeout")
        except Exception as e:
            logger.error(f"Finnhub quote error for {symbol}: {str(e)}")
            raise
    
    async def get_historical_data(self, symbol: str, period: str = "1mo") -> HistoricalData:
        """
        Fetch historical data from Finnhub.
        
        Args:
            symbol: Stock symbol
            period: Time period
            
        Returns:
            HistoricalData: Normalized historical data
        """
        finnhub_symbol = f"{self._convert_to_nse_symbol(symbol)}.NS"
        
        # Convert period to timestamps
        end_time = int(time.time())
        start_time = self._get_start_timestamp(period, end_time)
        
        params = {
            "symbol": finnhub_symbol,
            "resolution": self._get_resolution(period),
            "from": start_time,
            "to": end_time,
            "token": self.api_key or "demo"
        }
        
        url = f"{self.BASE_URL}/stock/candle"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    # Retry once
                    response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")
                
                data = response.json()
                
                if data.get("s") != "ok":
                    raise Exception(f"API Error: {data.get('s', 'Unknown error')}")
                
                return self._normalize_historical(data, symbol, period)
                
        except Exception as e:
            logger.error(f"Finnhub historical error for {symbol}: {str(e)}")
            raise
    
    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        """
        Fetch company profile from Finnhub.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            CompanyProfile: Normalized company data
        """
        finnhub_symbol = f"{self._convert_to_nse_symbol(symbol)}.NS"
        
        params = {
            "symbol": finnhub_symbol,
            "token": self.api_key or "demo"
        }
        
        url = f"{self.BASE_URL}/stock/profile2"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    # Retry once
                    response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")
                
                data = response.json()
                
                if not data:
                    raise Exception("No profile data available")
                
                return self._normalize_profile(data, symbol)
                
        except Exception as e:
            logger.error(f"Finnhub profile error for {symbol}: {str(e)}")
            raise
    
    async def _make_request(self, client: httpx.AsyncClient, url: str, params: Dict[str, Any]) -> httpx.Response:
        """Make HTTP request with structured logging"""
        logger.info(f"Finnhub API request: {url} with symbol {params.get('symbol')}")
        return await client.get(url, params=params)
    
    def _normalize_quote(self, data: Dict[str, Any], symbol: str) -> StockQuote:
        """Convert Finnhub quote response to normalized format"""
        try:
            # Finnhub response format: c=current, pc=previous_close, d=change, dp=percent_change
            current_price = float(data.get("c", 0))
            previous_close = float(data.get("pc", current_price))
            change = float(data.get("d", 0))
            percent_change = float(data.get("dp", 0))
            
            return StockQuote(
                symbol=symbol.upper(),
                price=round(current_price, 2),
                change=round(change, 2),
                percent_change=round(percent_change, 2),
                volume=int(data.get("v", 0)),  # Volume might not be available in quote
                timestamp=datetime.now().isoformat(),
                previous_close=round(previous_close, 2),
                currency="INR",
                exchange="NSE",
                market_state="UNKNOWN",  # Finnhub doesn't provide market state in quote
                is_demo=False
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error normalizing Finnhub quote: {e}")
            raise Exception("Invalid data format")
    
    def _normalize_historical(self, data: Dict[str, Any], symbol: str, period: str) -> HistoricalData:
        """Convert Finnhub historical response to normalized format"""
        try:
            # Finnhub response format: o=open, h=high, l=low, c=close, v=volume, t=timestamp
            opens = data.get("o", [])
            highs = data.get("h", [])
            lows = data.get("l", [])
            closes = data.get("c", [])
            volumes = data.get("v", [])
            timestamps = data.get("t", [])
            
            normalized_data = []
            
            for i in range(len(timestamps)):
                date = datetime.fromtimestamp(timestamps[i]).strftime("%Y-%m-%d")
                normalized_data.append({
                    "date": date,
                    "open": float(opens[i]) if i < len(opens) else 0,
                    "high": float(highs[i]) if i < len(highs) else 0,
                    "low": float(lows[i]) if i < len(lows) else 0,
                    "close": float(closes[i]) if i < len(closes) else 0,
                    "volume": int(volumes[i]) if i < len(volumes) else 0
                })
            
            return HistoricalData(
                symbol=symbol.upper(),
                data=normalized_data,
                period=period,
                is_demo=False
            )
        except (ValueError, TypeError, IndexError) as e:
            logger.error(f"Error normalizing Finnhub historical: {e}")
            raise Exception("Invalid data format")
    
    def _normalize_profile(self, data: Dict[str, Any], symbol: str) -> CompanyProfile:
        """Convert Finnhub profile response to normalized format"""
        try:
            market_cap = data.get("marketCapitalization")
            market_cap_float = float(market_cap) * 1000000 if market_cap else None  # Finnhub returns in millions
            
            return CompanyProfile(
                symbol=symbol.upper(),
                name=data.get("name", symbol.upper()),
                description=data.get("description"),
                sector=data.get("finnhubIndustry"),  # Finnhub uses different field names
                industry=data.get("gsubind"),
                market_cap=market_cap_float,
                market_cap_formatted=self._format_large_number(market_cap_float),
                employees=data.get("employeeTotal"),
                website=data.get("weburl"),
                is_demo=False
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error normalizing Finnhub profile: {e}")
            raise Exception("Invalid data format")
    
    def _get_start_timestamp(self, period: str, end_time: int) -> int:
        """Convert period to start timestamp"""
        now = datetime.fromtimestamp(end_time)
        
        period_map = {
            "1d": timedelta(days=1),
            "5d": timedelta(days=5),
            "1mo": timedelta(days=30),
            "3mo": timedelta(days=90),
            "6mo": timedelta(days=180),
            "1y": timedelta(days=365),
            "2y": timedelta(days=730),
            "5y": timedelta(days=1825),
            "10y": timedelta(days=3650),
            "ytd": timedelta(days=365),  # Approximate
            "max": timedelta(days=3650)  # 10 years max
        }
        
        delta = period_map.get(period, timedelta(days=30))
        start_date = now - delta
        return int(start_date.timestamp())
    
    def _get_resolution(self, period: str) -> str:
        """Get appropriate resolution for period"""
        if period in ["1d"]:
            return "5"  # 5-minute intervals
        elif period in ["5d"]:
            return "15"  # 15-minute intervals
        elif period in ["1mo", "3mo"]:
            return "D"  # Daily
        elif period in ["6mo", "1y"]:
            return "D"  # Daily
        else:
            return "W"  # Weekly for longer periods