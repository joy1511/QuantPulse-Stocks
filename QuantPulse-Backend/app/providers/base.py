"""
Base Stock Provider Interface

Defines the abstract interface that all stock data providers must implement.
This ensures consistent behavior and response formats across different providers.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import datetime
from pydantic import BaseModel


class StockQuote(BaseModel):
    """Normalized stock quote response schema"""
    symbol: str
    price: float
    change: float
    percent_change: float
    volume: int
    timestamp: str
    is_demo: bool = False
    currency: str = "INR"
    exchange: str = "NSE"
    market_state: str = "UNKNOWN"
    previous_close: float = 0.0


class CompanyProfile(BaseModel):
    """Normalized company profile response schema"""
    symbol: str
    name: str
    description: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[float] = None
    market_cap_formatted: Optional[str] = None
    employees: Optional[int] = None
    website: Optional[str] = None
    is_demo: bool = False


class HistoricalData(BaseModel):
    """Normalized historical data response schema"""
    symbol: str
    data: List[Dict[str, Any]]  # List of OHLCV data points
    period: str
    is_demo: bool = False


class BaseStockProvider(ABC):
    """
    Abstract base class for all stock data providers.
    
    All providers must implement these methods and return normalized responses
    that match the defined schemas above.
    """
    
    def __init__(self, api_key: Optional[str] = None, timeout: int = 8):
        self.api_key = api_key
        self.timeout = timeout
        self.provider_name = self.__class__.__name__
    
    @abstractmethod
    async def get_stock_quote(self, symbol: str) -> StockQuote:
        """
        Fetch current stock quote data.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            
        Returns:
            StockQuote: Normalized quote data
            
        Raises:
            Exception: If data cannot be fetched
        """
        pass
    
    @abstractmethod
    async def get_historical_data(
        self, 
        symbol: str, 
        period: str = "1mo"
    ) -> HistoricalData:
        """
        Fetch historical stock data.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            HistoricalData: Normalized historical data
            
        Raises:
            Exception: If data cannot be fetched
        """
        pass
    
    @abstractmethod
    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        """
        Fetch company profile information.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            
        Returns:
            CompanyProfile: Normalized company data
            
        Raises:
            Exception: If data cannot be fetched
        """
        pass
    
    def _convert_to_nse_symbol(self, symbol: str) -> str:
        """
        Convert plain symbol to NSE format if needed.
        
        Args:
            symbol: Plain stock symbol
            
        Returns:
            str: NSE formatted symbol
        """
        clean_symbol = symbol.strip().upper()
        if clean_symbol.endswith(".NS") or clean_symbol.endswith(".BO"):
            clean_symbol = clean_symbol[:-3]
        return clean_symbol
    
    def _format_large_number(self, value: Optional[float]) -> str:
        """Format large numbers in Indian style (Lakhs, Crores)"""
        if value is None:
            return "N/A"
        
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
    
    def _format_volume(self, volume: Optional[int]) -> str:
        """Format trading volume in millions/thousands"""
        if volume is None:
            return "N/A"
        
        if volume >= 1e6:
            return f"{volume / 1e6:.2f}M"
        elif volume >= 1e3:
            return f"{volume / 1e3:.1f}K"
        else:
            return str(volume)