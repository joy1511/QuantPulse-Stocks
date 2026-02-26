"""
Twelve Data Provider

Primary stock data provider using Twelve Data API.
Provides real-time quotes, historical data, and company profiles.
"""

import httpx
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .base import BaseStockProvider, StockQuote, CompanyProfile, HistoricalData

logger = logging.getLogger(__name__)


class TwelveDataProvider(BaseStockProvider):
    """
    Twelve Data API provider for stock market data.
    
    Features:
    - Real-time quotes
    - Historical data
    - Company profiles
    - Async HTTP requests with timeout protection
    - Automatic retry logic
    """
    
    BASE_URL = "https://api.twelvedata.com"
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 8):
        super().__init__(api_key, timeout)
        self.provider_name = "TwelveData"
    
    async def get_stock_quote(self, symbol: str) -> StockQuote:
        """
        Fetch real-time stock quote from Twelve Data.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            
        Returns:
            StockQuote: Normalized quote data
        """
        nse_symbol = f"{self._convert_to_nse_symbol(symbol)}.NSE"
        
        params = {
            "symbol": nse_symbol,
            "apikey": self.api_key or "demo"
        }
        
        url = f"{self.BASE_URL}/quote"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # First attempt
                response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    # Retry once
                    logger.warning(f"TwelveData first attempt failed: {response.status_code}")
                    response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                
                data = response.json()
                
                # Check for API error
                if "error" in data or "status" in data:
                    raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
                
                return self._normalize_quote(data, symbol)
                
        except httpx.TimeoutException:
            logger.error(f"TwelveData timeout for symbol: {symbol}")
            raise Exception("Request timeout")
        except Exception as e:
            logger.error(f"TwelveData quote error for {symbol}: {str(e)}")
            raise
    
    async def get_historical_data(self, symbol: str, period: str = "1mo") -> HistoricalData:
        """
        Fetch historical data from Twelve Data.
        
        Args:
            symbol: Stock symbol
            period: Time period
            
        Returns:
            HistoricalData: Normalized historical data
        """
        nse_symbol = f"{self._convert_to_nse_symbol(symbol)}.NSE"
        
        # Convert period to Twelve Data format
        interval, outputsize = self._convert_period(period)
        
        params = {
            "symbol": nse_symbol,
            "interval": interval,
            "outputsize": outputsize,
            "apikey": self.api_key or "demo"
        }
        
        url = f"{self.BASE_URL}/time_series"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    # Retry once
                    response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")
                
                data = response.json()
                
                if "error" in data or "status" in data:
                    raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
                
                return self._normalize_historical(data, symbol, period)
                
        except Exception as e:
            logger.error(f"TwelveData historical error for {symbol}: {str(e)}")
            raise
    
    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        """
        Fetch company profile from Twelve Data.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            CompanyProfile: Normalized company data
        """
        nse_symbol = f"{self._convert_to_nse_symbol(symbol)}.NSE"
        
        params = {
            "symbol": nse_symbol,
            "apikey": self.api_key or "demo"
        }
        
        url = f"{self.BASE_URL}/profile"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    # Retry once
                    response = await self._make_request(client, url, params)
                
                if response.status_code != 200:
                    raise Exception(f"HTTP {response.status_code}")
                
                data = response.json()
                
                if "error" in data or "status" in data:
                    raise Exception(f"API Error: {data.get('message', 'Unknown error')}")
                
                return self._normalize_profile(data, symbol)
                
        except Exception as e:
            logger.error(f"TwelveData profile error for {symbol}: {str(e)}")
            raise
    
    async def _make_request(self, client: httpx.AsyncClient, url: str, params: Dict[str, Any]) -> httpx.Response:
        """Make HTTP request with structured logging"""
        logger.info(f"TwelveData API request: {url} with symbol {params.get('symbol')}")
        return await client.get(url, params=params)
    
    def _normalize_quote(self, data: Dict[str, Any], symbol: str) -> StockQuote:
        """Convert Twelve Data quote response to normalized format"""
        try:
            price = float(data.get("close", 0))
            previous_close = float(data.get("previous_close", price))
            change = price - previous_close
            percent_change = (change / previous_close * 100) if previous_close else 0
            
            return StockQuote(
                symbol=symbol.upper(),
                price=round(price, 2),
                change=round(change, 2),
                percent_change=round(percent_change, 2),
                volume=int(data.get("volume", 0)),
                timestamp=datetime.now().isoformat(),
                previous_close=round(previous_close, 2),
                currency="INR",
                exchange="NSE",
                market_state=data.get("market_state", "UNKNOWN"),
                is_demo=False
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error normalizing TwelveData quote: {e}")
            raise Exception("Invalid data format")
    
    def _normalize_historical(self, data: Dict[str, Any], symbol: str, period: str) -> HistoricalData:
        """Convert Twelve Data historical response to normalized format"""
        try:
            values = data.get("values", [])
            normalized_data = []
            
            for item in values:
                normalized_data.append({
                    "date": item.get("datetime"),
                    "open": float(item.get("open", 0)),
                    "high": float(item.get("high", 0)),
                    "low": float(item.get("low", 0)),
                    "close": float(item.get("close", 0)),
                    "volume": int(item.get("volume", 0))
                })
            
            return HistoricalData(
                symbol=symbol.upper(),
                data=normalized_data,
                period=period,
                is_demo=False
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error normalizing TwelveData historical: {e}")
            raise Exception("Invalid data format")
    
    def _normalize_profile(self, data: Dict[str, Any], symbol: str) -> CompanyProfile:
        """Convert Twelve Data profile response to normalized format"""
        try:
            market_cap = data.get("market_capitalization")
            market_cap_float = float(market_cap) if market_cap else None
            
            return CompanyProfile(
                symbol=symbol.upper(),
                name=data.get("name", symbol.upper()),
                description=data.get("description"),
                sector=data.get("sector"),
                industry=data.get("industry"),
                market_cap=market_cap_float,
                market_cap_formatted=self._format_large_number(market_cap_float),
                employees=data.get("employees"),
                website=data.get("website"),
                is_demo=False
            )
        except (ValueError, TypeError) as e:
            logger.error(f"Error normalizing TwelveData profile: {e}")
            raise Exception("Invalid data format")
    
    def _convert_period(self, period: str) -> tuple[str, str]:
        """Convert standard period to Twelve Data interval and outputsize"""
        period_map = {
            "1d": ("1min", "78"),      # 1 day of 1-minute data
            "5d": ("5min", "288"),     # 5 days of 5-minute data
            "1mo": ("1day", "30"),     # 1 month of daily data
            "3mo": ("1day", "90"),     # 3 months of daily data
            "6mo": ("1day", "180"),    # 6 months of daily data
            "1y": ("1day", "365"),     # 1 year of daily data
            "2y": ("1week", "104"),    # 2 years of weekly data
            "5y": ("1week", "260"),    # 5 years of weekly data
            "10y": ("1month", "120"),  # 10 years of monthly data
            "ytd": ("1day", "250"),    # Year to date
            "max": ("1month", "5000")  # Maximum available
        }
        
        return period_map.get(period, ("1day", "30"))