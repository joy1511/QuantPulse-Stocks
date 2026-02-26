"""
Demo Data Service

Generates realistic simulated stock data when live providers fail.
Ensures the user experience never breaks due to API failures.
"""

import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any
import math

from ..providers.base import StockQuote, CompanyProfile, HistoricalData

logger = logging.getLogger(__name__)


class DemoDataService:
    """
    Service for generating realistic demo stock data.
    
    Features:
    - Realistic price movements based on volatility
    - Believable volume ranges
    - Proper market cap calculations
    - Company profiles with Indian context
    - Historical data generation
    """
    
    # Base data for popular NSE stocks
    STOCK_DATABASE = {
        "RELIANCE": {
            "name": "Reliance Industries Limited",
            "base_price": 2950.0,
            "volatility": 0.02,  # 2% daily volatility
            "volume_range": (5000000, 15000000),
            "market_cap": 19500000000000,  # 19.5 Lakh Crores
            "sector": "Oil & Gas",
            "industry": "Refineries",
            "description": "India's largest private sector company with interests in petrochemicals, oil & gas, telecom and retail."
        },
        "TCS": {
            "name": "Tata Consultancy Services Limited",
            "base_price": 4200.0,
            "volatility": 0.015,
            "volume_range": (2000000, 8000000),
            "market_cap": 15400000000000,  # 15.4 Lakh Crores
            "sector": "Information Technology",
            "industry": "IT Services",
            "description": "Leading global IT services, consulting and business solutions organization."
        },
        "HDFCBANK": {
            "name": "HDFC Bank Limited",
            "base_price": 1750.0,
            "volatility": 0.018,
            "volume_range": (3000000, 12000000),
            "market_cap": 13200000000000,  # 13.2 Lakh Crores
            "sector": "Financial Services",
            "industry": "Private Sector Bank",
            "description": "India's largest private sector bank offering a wide range of banking and financial services."
        },
        "INFY": {
            "name": "Infosys Limited",
            "base_price": 1850.0,
            "volatility": 0.02,
            "volume_range": (4000000, 10000000),
            "market_cap": 7800000000000,  # 7.8 Lakh Crores
            "sector": "Information Technology",
            "industry": "IT Services",
            "description": "Global leader in next-generation digital services and consulting."
        },
        "ICICIBANK": {
            "name": "ICICI Bank Limited",
            "base_price": 1250.0,
            "volatility": 0.022,
            "volume_range": (8000000, 20000000),
            "market_cap": 8700000000000,  # 8.7 Lakh Crores
            "sector": "Financial Services",
            "industry": "Private Sector Bank",
            "description": "India's second-largest private sector bank providing comprehensive financial services."
        },
        "BHARTIARTL": {
            "name": "Bharti Airtel Limited",
            "base_price": 1650.0,
            "volatility": 0.025,
            "volume_range": (6000000, 18000000),
            "market_cap": 9200000000000,  # 9.2 Lakh Crores
            "sector": "Telecommunication",
            "industry": "Telecom Services",
            "description": "Leading telecommunications company providing mobile, broadband and digital services."
        },
        "ITC": {
            "name": "ITC Limited",
            "base_price": 485.0,
            "volatility": 0.015,
            "volume_range": (10000000, 25000000),
            "market_cap": 6000000000000,  # 6 Lakh Crores
            "sector": "FMCG",
            "industry": "Diversified FMCG",
            "description": "Leading Indian conglomerate with interests in FMCG, hotels, paperboards and agri-business."
        },
        "SBIN": {
            "name": "State Bank of India",
            "base_price": 850.0,
            "volatility": 0.025,
            "volume_range": (15000000, 35000000),
            "market_cap": 7600000000000,  # 7.6 Lakh Crores
            "sector": "Financial Services",
            "industry": "Public Sector Bank",
            "description": "India's largest public sector bank providing comprehensive banking services."
        },
        "LT": {
            "name": "Larsen & Toubro Limited",
            "base_price": 3650.0,
            "volatility": 0.02,
            "volume_range": (1500000, 5000000),
            "market_cap": 5100000000000,  # 5.1 Lakh Crores
            "sector": "Construction",
            "industry": "Engineering & Construction",
            "description": "Leading Indian multinational engaged in EPC projects, hi-tech manufacturing and services."
        },
        "HCLTECH": {
            "name": "HCL Technologies Limited",
            "base_price": 1580.0,
            "volatility": 0.022,
            "volume_range": (2500000, 7000000),
            "market_cap": 4300000000000,  # 4.3 Lakh Crores
            "sector": "Information Technology",
            "industry": "IT Services",
            "description": "Leading global technology company providing IT services and solutions."
        }
    }
    
    def __init__(self):
        self.price_cache = {}  # Cache for consistent demo prices
        logger.info("Demo data service initialized")
    
    async def get_demo_quote(self, symbol: str) -> StockQuote:
        """
        Generate realistic demo stock quote.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            StockQuote: Simulated quote data with is_demo=True
        """
        logger.warning(f"Serving demo data for stock quote: {symbol}")
        
        stock_info = self._get_stock_info(symbol)
        
        # Generate realistic price movement
        current_price = self._generate_realistic_price(symbol, stock_info)
        previous_close = stock_info["base_price"]
        
        # Calculate changes
        change = current_price - previous_close
        percent_change = (change / previous_close) * 100
        
        # Generate realistic volume
        volume = random.randint(*stock_info["volume_range"])
        
        return StockQuote(
            symbol=symbol.upper(),
            price=round(current_price, 2),
            change=round(change, 2),
            percent_change=round(percent_change, 2),
            volume=volume,
            timestamp=datetime.now().isoformat(),
            previous_close=round(previous_close, 2),
            currency="INR",
            exchange="NSE",
            market_state="REGULAR",
            is_demo=True
        )
    
    async def get_demo_historical(self, symbol: str, period: str = "1mo") -> HistoricalData:
        """
        Generate realistic demo historical data.
        
        Args:
            symbol: Stock symbol
            period: Time period
            
        Returns:
            HistoricalData: Simulated historical data with is_demo=True
        """
        logger.warning(f"Serving demo historical data for: {symbol} ({period})")
        
        stock_info = self._get_stock_info(symbol)
        base_price = stock_info["base_price"]
        volatility = stock_info["volatility"]
        
        # Generate historical data points
        data_points = self._generate_historical_points(base_price, volatility, period)
        
        return HistoricalData(
            symbol=symbol.upper(),
            data=data_points,
            period=period,
            is_demo=True
        )
    
    async def get_demo_profile(self, symbol: str) -> CompanyProfile:
        """
        Generate realistic demo company profile.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            CompanyProfile: Simulated company data with is_demo=True
        """
        logger.warning(f"Serving demo profile data for: {symbol}")
        
        stock_info = self._get_stock_info(symbol)
        
        return CompanyProfile(
            symbol=symbol.upper(),
            name=stock_info["name"],
            description=stock_info["description"],
            sector=stock_info["sector"],
            industry=stock_info["industry"],
            market_cap=stock_info["market_cap"],
            market_cap_formatted=self._format_large_number(stock_info["market_cap"]),
            employees=random.randint(50000, 500000),
            website=f"https://www.{symbol.lower()}.com",
            is_demo=True
        )
    
    def _get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get stock info from database or generate generic data"""
        symbol_upper = symbol.upper()
        
        if symbol_upper in self.STOCK_DATABASE:
            return self.STOCK_DATABASE[symbol_upper]
        
        # Generate generic data for unknown symbols
        return {
            "name": f"{symbol_upper} Limited",
            "base_price": random.uniform(100, 5000),
            "volatility": random.uniform(0.015, 0.03),
            "volume_range": (1000000, 10000000),
            "market_cap": random.uniform(1e11, 1e13),  # 1 Lakh Cr to 10 Lakh Cr
            "sector": random.choice(["Technology", "Finance", "Healthcare", "Energy", "Consumer Goods"]),
            "industry": "Diversified",
            "description": f"{symbol_upper} is a leading company in its sector with strong market presence."
        }
    
    def _generate_realistic_price(self, symbol: str, stock_info: Dict[str, Any]) -> float:
        """Generate realistic price with controlled volatility"""
        base_price = stock_info["base_price"]
        volatility = stock_info["volatility"]
        
        # Use cached price for consistency within short time periods
        cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d_%H')}"  # Hourly cache
        
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]
        
        # Generate price movement using normal distribution
        # Most movements will be small, with occasional larger moves
        price_change_percent = random.gauss(0, volatility)  # Mean=0, StdDev=volatility
        
        # Limit extreme movements (circuit breakers)
        price_change_percent = max(-0.05, min(0.05, price_change_percent))  # ±5% max
        
        new_price = base_price * (1 + price_change_percent)
        
        # Ensure price stays within reasonable bounds
        min_price = base_price * 0.8  # 20% below base
        max_price = base_price * 1.2  # 20% above base
        new_price = max(min_price, min(max_price, new_price))
        
        # Cache the price
        self.price_cache[cache_key] = new_price
        
        return new_price
    
    def _generate_historical_points(self, base_price: float, volatility: float, period: str) -> List[Dict[str, Any]]:
        """Generate realistic historical OHLCV data"""
        # Determine number of data points based on period
        days_map = {
            "1d": 1,
            "5d": 5,
            "1mo": 30,
            "3mo": 90,
            "6mo": 180,
            "1y": 365,
            "2y": 730,
            "5y": 1825,
            "10y": 3650,
            "ytd": 250,  # Approximate trading days YTD
            "max": 1825  # 5 years
        }
        
        days = days_map.get(period, 30)
        data_points = []
        
        current_price = base_price
        current_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            # Generate daily price movement
            daily_change = random.gauss(0, volatility)
            daily_change = max(-0.05, min(0.05, daily_change))  # Limit to ±5%
            
            # Calculate OHLC
            open_price = current_price
            close_price = open_price * (1 + daily_change)
            
            # High and low based on intraday volatility
            intraday_volatility = volatility * 0.5
            high_price = max(open_price, close_price) * (1 + abs(random.gauss(0, intraday_volatility)))
            low_price = min(open_price, close_price) * (1 - abs(random.gauss(0, intraday_volatility)))
            
            # Ensure logical OHLC relationship
            high_price = max(high_price, open_price, close_price)
            low_price = min(low_price, open_price, close_price)
            
            # Generate volume (higher volume on bigger price moves)
            base_volume = random.randint(1000000, 5000000)
            volume_multiplier = 1 + abs(daily_change) * 10  # Higher volume on big moves
            volume = int(base_volume * volume_multiplier)
            
            data_points.append({
                "date": current_date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })
            
            # Update for next day
            current_price = close_price
            current_date += timedelta(days=1)
        
        return data_points
    
    def _format_large_number(self, value: float) -> str:
        """Format large numbers in Indian style (Lakhs, Crores)"""
        if value >= 1e12:  # Lakh Crores
            return f"₹{value / 1e12:.2f}L Cr"
        elif value >= 1e9:  # Thousands Crores
            return f"₹{value / 1e7:.0f} Cr"
        elif value >= 1e7:  # Crores
            return f"₹{value / 1e7:.2f} Cr"
        elif value >= 1e5:  # Lakhs
            return f"₹{value / 1e5:.2f}L"
        else:
            return f"₹{value:,.0f}"