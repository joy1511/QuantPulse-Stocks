"""
Provider Factory

Smart factory that manages provider selection, fallback logic, and failure handling.
Implements the complete provider chain: Primary → Fallback → Demo Data.
"""

import logging
from typing import Optional, Union
from enum import Enum

from ..config import TWELVEDATA_API_KEY, FINNHUB_API_KEY, STOCK_PROVIDER
from .base import BaseStockProvider, StockQuote, CompanyProfile, HistoricalData
from .twelvedata_provider import TwelveDataProvider
from .finnhub_provider import FinnhubProvider

logger = logging.getLogger(__name__)


class ProviderMode(Enum):
    """Provider operation modes"""
    AUTO = "auto"           # Primary → Fallback → Demo
    TWELVEDATA = "twelvedata"  # Force primary only
    FINNHUB = "finnhub"     # Force fallback only
    DEMO = "demo"           # Force demo data only


class ProviderFactory:
    """
    Smart provider factory with automatic fallback logic.
    
    Features:
    - Automatic provider selection
    - Fallback chain management
    - Environment-based configuration
    - Structured logging
    - Demo mode support
    """
    
    def __init__(self):
        self.mode = self._get_provider_mode()
        self.primary_provider = self._create_primary_provider()
        self.fallback_provider = self._create_fallback_provider()
        
        logger.info(f"Provider factory initialized in {self.mode.value} mode")
    
    async def get_stock_quote(self, symbol: str) -> StockQuote:
        """
        Get stock quote with automatic fallback logic.
        
        Flow:
        1. Try primary provider (Twelve Data)
        2. If fails, try fallback provider (Finnhub)
        3. If both fail, return demo data
        
        Args:
            symbol: Stock symbol
            
        Returns:
            StockQuote: Normalized quote data (may be demo)
        """
        if self.mode == ProviderMode.DEMO:
            logger.info(f"Demo mode: returning simulated data for {symbol}")
            return await self._get_demo_quote(symbol)
        
        if self.mode == ProviderMode.FINNHUB:
            return await self._try_fallback_quote(symbol)
        
        if self.mode == ProviderMode.TWELVEDATA:
            return await self._try_primary_quote(symbol)
        
        # AUTO mode: full fallback chain
        try:
            return await self._try_primary_quote(symbol)
        except Exception as e:
            logger.warning(f"Primary provider failed for {symbol}: {str(e)}")
            try:
                return await self._try_fallback_quote(symbol)
            except Exception as e2:
                logger.warning(f"Fallback provider failed for {symbol}: {str(e2)}")
                logger.warning(f"All providers failed for {symbol} - serving demo data")
                return await self._get_demo_quote(symbol)
    
    async def get_historical_data(self, symbol: str, period: str = "1mo") -> HistoricalData:
        """
        Get historical data with automatic fallback logic.
        
        Args:
            symbol: Stock symbol
            period: Time period
            
        Returns:
            HistoricalData: Normalized historical data (may be demo)
        """
        if self.mode == ProviderMode.DEMO:
            logger.info(f"Demo mode: returning simulated historical data for {symbol}")
            return await self._get_demo_historical(symbol, period)
        
        if self.mode == ProviderMode.FINNHUB:
            return await self._try_fallback_historical(symbol, period)
        
        if self.mode == ProviderMode.TWELVEDATA:
            return await self._try_primary_historical(symbol, period)
        
        # AUTO mode: full fallback chain
        try:
            return await self._try_primary_historical(symbol, period)
        except Exception as e:
            logger.warning(f"Primary provider historical failed for {symbol}: {str(e)}")
            try:
                return await self._try_fallback_historical(symbol, period)
            except Exception as e2:
                logger.warning(f"Fallback provider historical failed for {symbol}: {str(e2)}")
                logger.warning(f"All providers failed for {symbol} historical - serving demo data")
                return await self._get_demo_historical(symbol, period)
    
    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        """
        Get company profile with automatic fallback logic.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            CompanyProfile: Normalized company data (may be demo)
        """
        if self.mode == ProviderMode.DEMO:
            logger.info(f"Demo mode: returning simulated profile for {symbol}")
            return await self._get_demo_profile(symbol)
        
        if self.mode == ProviderMode.FINNHUB:
            return await self._try_fallback_profile(symbol)
        
        if self.mode == ProviderMode.TWELVEDATA:
            return await self._try_primary_profile(symbol)
        
        # AUTO mode: full fallback chain
        try:
            return await self._try_primary_profile(symbol)
        except Exception as e:
            logger.warning(f"Primary provider profile failed for {symbol}: {str(e)}")
            try:
                return await self._try_fallback_profile(symbol)
            except Exception as e2:
                logger.warning(f"Fallback provider profile failed for {symbol}: {str(e2)}")
                logger.warning(f"All providers failed for {symbol} profile - serving demo data")
                return await self._get_demo_profile(symbol)
    
    # Primary provider methods
    async def _try_primary_quote(self, symbol: str) -> StockQuote:
        """Try primary provider for quote"""
        if not self.primary_provider:
            raise Exception("Primary provider not available")
        return await self.primary_provider.get_stock_quote(symbol)
    
    async def _try_primary_historical(self, symbol: str, period: str) -> HistoricalData:
        """Try primary provider for historical data"""
        if not self.primary_provider:
            raise Exception("Primary provider not available")
        return await self.primary_provider.get_historical_data(symbol, period)
    
    async def _try_primary_profile(self, symbol: str) -> CompanyProfile:
        """Try primary provider for company profile"""
        if not self.primary_provider:
            raise Exception("Primary provider not available")
        return await self.primary_provider.get_company_profile(symbol)
    
    # Fallback provider methods
    async def _try_fallback_quote(self, symbol: str) -> StockQuote:
        """Try fallback provider for quote"""
        if not self.fallback_provider:
            raise Exception("Fallback provider not available")
        logger.warning(f"Using fallback provider for {symbol} quote")
        return await self.fallback_provider.get_stock_quote(symbol)
    
    async def _try_fallback_historical(self, symbol: str, period: str) -> HistoricalData:
        """Try fallback provider for historical data"""
        if not self.fallback_provider:
            raise Exception("Fallback provider not available")
        logger.warning(f"Using fallback provider for {symbol} historical")
        return await self.fallback_provider.get_historical_data(symbol, period)
    
    async def _try_fallback_profile(self, symbol: str) -> CompanyProfile:
        """Try fallback provider for company profile"""
        if not self.fallback_provider:
            raise Exception("Fallback provider not available")
        logger.warning(f"Using fallback provider for {symbol} profile")
        return await self.fallback_provider.get_company_profile(symbol)
    
    # Demo data methods (will be implemented by demo service)
    async def _get_demo_quote(self, symbol: str) -> StockQuote:
        """Get demo quote data"""
        from ..services.demo_data_service import DemoDataService
        demo_service = DemoDataService()
        return await demo_service.get_demo_quote(symbol)
    
    async def _get_demo_historical(self, symbol: str, period: str) -> HistoricalData:
        """Get demo historical data"""
        from ..services.demo_data_service import DemoDataService
        demo_service = DemoDataService()
        return await demo_service.get_demo_historical(symbol, period)
    
    async def _get_demo_profile(self, symbol: str) -> CompanyProfile:
        """Get demo profile data"""
        from ..services.demo_data_service import DemoDataService
        demo_service = DemoDataService()
        return await demo_service.get_demo_profile(symbol)
    
    # Factory setup methods
    def _get_provider_mode(self) -> ProviderMode:
        """Get provider mode from configuration"""
        mode_str = STOCK_PROVIDER.lower()
        try:
            return ProviderMode(mode_str)
        except ValueError:
            logger.warning(f"Invalid STOCK_PROVIDER value: {mode_str}, defaulting to auto")
            return ProviderMode.AUTO
    
    def _create_primary_provider(self) -> Optional[TwelveDataProvider]:
        """Create primary provider (Twelve Data)"""
        if not TWELVEDATA_API_KEY and self.mode in [ProviderMode.AUTO, ProviderMode.TWELVEDATA]:
            logger.warning("TWELVEDATA_API_KEY not found - primary provider disabled")
            if self.mode == ProviderMode.TWELVEDATA:
                logger.error("Forced TwelveData mode but no API key provided")
                return None
        
        if TWELVEDATA_API_KEY:
            logger.info("Primary provider (TwelveData) initialized")
            return TwelveDataProvider(api_key=TWELVEDATA_API_KEY)
        
        return None
    
    def _create_fallback_provider(self) -> Optional[FinnhubProvider]:
        """Create fallback provider (Finnhub)"""
        if not FINNHUB_API_KEY and self.mode in [ProviderMode.AUTO, ProviderMode.FINNHUB]:
            logger.warning("FINNHUB_API_KEY not found - fallback provider disabled")
            if self.mode == ProviderMode.FINNHUB:
                logger.error("Forced Finnhub mode but no API key provided")
                return None
        
        if FINNHUB_API_KEY:
            logger.info("Fallback provider (Finnhub) initialized")
            return FinnhubProvider(api_key=FINNHUB_API_KEY)
        
        return None
    
    def get_provider_status(self) -> dict:
        """Get current provider status for debugging"""
        return {
            "mode": self.mode.value,
            "primary_available": self.primary_provider is not None,
            "fallback_available": self.fallback_provider is not None,
            "primary_provider": "TwelveData" if self.primary_provider else None,
            "fallback_provider": "Finnhub" if self.fallback_provider else None
        }