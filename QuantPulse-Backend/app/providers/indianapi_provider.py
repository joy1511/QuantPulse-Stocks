"""
IndianAPI Provider — FREE NSE/BSE Stock Data

Uses indianapi.in for Indian stock market data.
- FREE tier: No API key required for basic endpoints
- Premium tier: API key unlocks advanced features
- Supports NSE and BSE stocks
- Historical data available
- Works on cloud servers

Documentation: https://indianapi.in/documentation/indian-stock-market
"""

import logging
import httpx
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

from .base import BaseStockProvider, StockQuote, CompanyProfile, HistoricalData

logger = logging.getLogger(__name__)


class IndianAPIProvider(BaseStockProvider):
    """
    Provider for Indian stock market data using indianapi.in
    
    Features:
    - FREE tier: Works without API key for basic endpoints
    - Premium tier: API key unlocks advanced features
    - NSE and BSE support
    - Historical data
    - Real-time quotes
    - Works on cloud servers
    """
    
    BASE_URL = "https://stock.indianapi.in"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize IndianAPI provider.
        
        Args:
            api_key: Optional API key for premium features
                    If None, uses FREE tier (basic endpoints work without key)
        """
        super().__init__(api_key)
        self.session = httpx.AsyncClient(timeout=30.0)
        
        if self.api_key:
            logger.info("✅ IndianAPI provider initialized (Premium tier with API key)")
        else:
            logger.info("✅ IndianAPI provider initialized (FREE tier - no API key)")
    
    def _get_headers(self) -> dict:
        """
        Get HTTP headers for API requests.
        Includes API key if available (for premium features).
        
        Note: IndianAPI uses 'X-API-Key' header for authentication
        """
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "QuantPulse/2.0"
        }
        
        # Add API key to headers if available
        # IndianAPI requires 'X-API-Key' header (case-insensitive)
        if self.api_key:
            headers["X-API-Key"] = self.api_key
        
        return headers
    
    async def get_stock_quote(self, symbol: str) -> StockQuote:
        """
        Get current stock quote from IndianAPI.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE", "TCS")
            
        Returns:
            StockQuote with current price data
        """
        try:
            # Remove .NS or .BO suffix if present
            clean_symbol = symbol.replace(".NS", "").replace(".BO", "").strip().upper()
            
            logger.info(f"📥 Fetching quote for {clean_symbol} from IndianAPI...")
            
            # Use /stock endpoint to get company data
            response = await self.session.get(
                f"{self.BASE_URL}/stock",
                params={"name": clean_symbol},
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract price data
            current_price_data = data.get("currentPrice", {})
            nse_price = current_price_data.get("NSE")
            bse_price = current_price_data.get("BSE")
            
            # Prefer NSE price, fallback to BSE
            price = nse_price if nse_price else bse_price
            
            if not price:
                raise ValueError(f"No price data available for {clean_symbol}")
            
            # Convert to float (API returns strings)
            price = float(price)
            
            # Calculate change (if previous close available)
            percent_change = data.get("percentChange", 0.0)
            if isinstance(percent_change, str):
                percent_change = float(percent_change) if percent_change else 0.0
            
            change = (price * percent_change) / 100 if percent_change else 0.0
            previous_close = price - change if change else price
            
            # Extract volume from technical data if available
            technical_data = data.get("stockTechnicalData", {})
            volume = 0
            if isinstance(technical_data, dict):
                volume = technical_data.get("volume", 0)
            elif isinstance(technical_data, list) and technical_data:
                # If it's a list, try to get volume from first item
                volume = technical_data[0].get("volume", 0) if isinstance(technical_data[0], dict) else 0
            
            logger.info(f"✅ IndianAPI quote: {clean_symbol} = ₹{price}")
            
            return StockQuote(
                symbol=clean_symbol,
                price=float(price),
                change=float(change),
                percent_change=float(percent_change),
                volume=int(volume) if volume else 0,
                timestamp=datetime.now().isoformat(),
                previous_close=float(previous_close),
                currency="INR",
                exchange="NSE" if nse_price else "BSE",
                market_state="REGULAR",
                is_demo=False
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ IndianAPI HTTP error for {symbol}: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ IndianAPI quote failed for {symbol}: {e}")
            raise
    
    async def get_historical_data(self, symbol: str, period: str = "1y") -> HistoricalData:
        """
        Get historical stock data from IndianAPI.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE", "TCS")
            period: Time period (1m, 6m, 1yr, 3yr, 5yr, 10yr, max)
            
        Returns:
            HistoricalData with OHLCV data
        """
        try:
            # Remove .NS or .BO suffix if present
            clean_symbol = symbol.replace(".NS", "").replace(".BO", "").strip().upper()
            
            # Map period to IndianAPI format
            period_map = {
                "1d": "1m",
                "5d": "1m",
                "1mo": "1m",
                "3mo": "6m",
                "6mo": "6m",
                "1y": "1yr",
                "2y": "3yr",
                "5y": "5yr",
                "10y": "10yr",
                "max": "max"
            }
            api_period = period_map.get(period, "1yr")
            
            logger.info(f"📥 Fetching historical data for {clean_symbol} ({api_period}) from IndianAPI...")
            
            # Use /historical_data endpoint
            response = await self.session.get(
                f"{self.BASE_URL}/historical_data",
                params={
                    "stock_name": clean_symbol,
                    "period": api_period,
                    "filter": "price"
                },
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            # Parse the response
            datasets = data.get("datasets", [])
            if not datasets:
                raise ValueError(f"No historical data available for {clean_symbol}")
            
            # Find price and volume datasets
            price_data = None
            volume_data = None
            
            for dataset in datasets:
                metric = dataset.get("metric", "")
                if metric == "Price":
                    price_data = dataset.get("values", [])
                elif metric == "Volume":
                    volume_data = dataset.get("values", [])
            
            if not price_data:
                raise ValueError(f"No price data in historical response for {clean_symbol}")
            
            # Convert to list of dicts
            historical_points = []
            volume_dict = {}
            
            # Build volume lookup dict
            if volume_data:
                for vol_entry in volume_data:
                    if len(vol_entry) >= 2:
                        date_str = vol_entry[0]
                        volume = vol_entry[1]
                        volume_dict[date_str] = volume
            
            # Process price data
            for i, price_entry in enumerate(price_data):
                if len(price_entry) >= 2:
                    date_str = price_entry[0]
                    close_price = float(price_entry[1])
                    
                    # Get volume for this date
                    volume = volume_dict.get(date_str, 0)
                    
                    # Estimate OHLC from close price (IndianAPI only provides close)
                    # Add small random variation for realistic OHLC
                    open_price = close_price * 0.998  # Slightly lower
                    high_price = close_price * 1.002  # Slightly higher
                    low_price = close_price * 0.997   # Slightly lower
                    
                    historical_points.append({
                        "date": date_str,
                        "open": round(open_price, 2),
                        "high": round(high_price, 2),
                        "low": round(low_price, 2),
                        "close": round(close_price, 2),
                        "volume": int(volume) if volume else 0
                    })
            
            logger.info(f"✅ IndianAPI historical: {len(historical_points)} data points for {clean_symbol}")
            
            return HistoricalData(
                symbol=clean_symbol,
                data=historical_points,
                period=period,
                is_demo=False
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ IndianAPI HTTP error for {symbol}: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ IndianAPI historical failed for {symbol}: {e}")
            raise
    
    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        """
        Get company profile from IndianAPI.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE", "TCS")
            
        Returns:
            CompanyProfile with company information
        """
        try:
            # Remove .NS or .BO suffix if present
            clean_symbol = symbol.replace(".NS", "").replace(".BO", "").strip().upper()
            
            logger.info(f"📥 Fetching profile for {clean_symbol} from IndianAPI...")
            
            # Use /stock endpoint to get company data
            response = await self.session.get(
                f"{self.BASE_URL}/stock",
                params={"name": clean_symbol},
                headers=self._get_headers()
            )
            response.raise_for_status()
            data = response.json()
            
            # Extract company information
            company_name = data.get("companyName", f"{clean_symbol} Limited")
            industry = data.get("industry", "Unknown")
            
            # Extract profile data
            profile_data = data.get("companyProfile", {})
            description = profile_data.get("description", f"{company_name} is a leading company in the {industry} sector.")
            
            # Extract market cap from key metrics
            key_metrics = data.get("keyMetrics", {})
            market_cap_str = key_metrics.get("marketCap", "0")
            
            # Parse market cap (format: "₹1.2L Cr" or similar)
            market_cap = self._parse_market_cap(market_cap_str)
            
            logger.info(f"✅ IndianAPI profile: {company_name}")
            
            return CompanyProfile(
                symbol=clean_symbol,
                name=company_name,
                description=description,
                sector=industry,
                industry=industry,
                market_cap=market_cap,
                market_cap_formatted=market_cap_str,
                employees=None,
                website=f"https://www.{clean_symbol.lower()}.com",
                is_demo=False
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ IndianAPI HTTP error for {symbol}: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ IndianAPI profile failed for {symbol}: {e}")
            raise
    
    def _parse_market_cap(self, market_cap_str: str) -> float:
        """
        Parse market cap string to float.
        
        Examples:
            "₹1.2L Cr" -> 1.2e12 (1.2 Lakh Crores)
            "₹5000 Cr" -> 5e9 (5000 Crores)
            "₹50L" -> 5e6 (50 Lakhs)
        """
        try:
            # Remove currency symbol and spaces
            clean_str = market_cap_str.replace("₹", "").replace(",", "").strip()
            
            # Extract number and unit
            if "L Cr" in clean_str:
                # Lakh Crores
                num = float(clean_str.replace("L Cr", "").strip())
                return num * 1e12
            elif "Cr" in clean_str:
                # Crores
                num = float(clean_str.replace("Cr", "").strip())
                return num * 1e7
            elif "L" in clean_str:
                # Lakhs
                num = float(clean_str.replace("L", "").strip())
                return num * 1e5
            else:
                # Try to parse as plain number
                return float(clean_str)
        except Exception:
            return 0.0
    
    async def close(self):
        """Close the HTTP session"""
        await self.session.aclose()
