"""
Provider Factory

Smart factory that manages provider selection, fallback logic, and failure handling.
Implements the complete provider chain: IndianAPI (Primary) → Demo Data.

TwelveData and Finnhub are available but disabled by default in AUTO mode
because they do not support Indian market symbols properly.
They can be force-enabled via STOCK_PROVIDER env var.
"""

import logging
from typing import Optional, Union
from enum import Enum

from ..config import TWELVEDATA_API_KEY, FINNHUB_API_KEY, INDIANAPI_KEY, STOCK_PROVIDER
from .base import BaseStockProvider, StockQuote, CompanyProfile, HistoricalData

logger = logging.getLogger(__name__)


class ProviderMode(Enum):
    """Provider operation modes"""
    AUTO = "auto"               # IndianAPI → Demo
    INDIANAPI = "indianapi"     # Force IndianAPI only
    TWELVEDATA = "twelvedata"   # Force TwelveData only
    FINNHUB = "finnhub"         # Force Finnhub only
    DEMO = "demo"               # Force demo data only


class ProviderFactory:
    """
    Smart provider factory with automatic fallback logic.
    
    Default chain (AUTO mode): IndianAPI → Demo Data
    
    TwelveData and Finnhub are NOT used in AUTO mode because:
    - TwelveData does not support .NSE suffix for Indian stocks
    - Finnhub returns 403 for Indian market (.NS) symbols
    
    They can be force-enabled via STOCK_PROVIDER=twelvedata or STOCK_PROVIDER=finnhub.
    """
    
    def __init__(self):
        self.mode = self._get_provider_mode()
        self.primary_provider = self._create_primary_provider()
        self.fallback_provider = self._create_fallback_provider()
        
        logger.info(f"Provider factory initialized in {self.mode.value} mode")
    
    async def get_stock_quote(self, symbol: str) -> StockQuote:
        """
        Get stock quote with automatic fallback logic.
        
        Flow (AUTO mode):
        1. Try IndianAPI (works for all NSE/BSE stocks)
        2. If fails, return demo data
        
        Args:
            symbol: Stock symbol
            
        Returns:
            StockQuote: Normalized quote data (may be demo)
        """
        if self.mode == ProviderMode.DEMO:
            logger.info(f"Demo mode: returning simulated data for {symbol}")
            return await self._get_demo_quote(symbol)
        
        # For forced TwelveData or Finnhub modes, use fallback_provider
        if self.mode in [ProviderMode.TWELVEDATA, ProviderMode.FINNHUB]:
            if self.fallback_provider:
                try:
                    return await self.fallback_provider.get_stock_quote(symbol)
                except Exception as e:
                    logger.warning(f"Forced provider failed for {symbol}: {e}")
                    return await self._get_demo_quote(symbol)
            return await self._get_demo_quote(symbol)
        
        # AUTO / INDIANAPI mode: IndianAPI → Demo
        try:
            return await self._try_primary_quote(symbol)
        except Exception as e:
            logger.warning(f"Primary provider (IndianAPI) failed for {symbol}: {str(e)}")
            logger.warning(f"Falling back to demo data for {symbol}")
            return await self._get_demo_quote(symbol)
    
    async def get_historical_data(self, symbol: str, period: str = "1mo") -> HistoricalData:
        """
        Get historical data with automatic fallback logic.
        """
        if self.mode == ProviderMode.DEMO:
            return await self._get_demo_historical(symbol, period)
        
        if self.mode in [ProviderMode.TWELVEDATA, ProviderMode.FINNHUB]:
            if self.fallback_provider:
                try:
                    return await self.fallback_provider.get_historical_data(symbol, period)
                except Exception as e:
                    logger.warning(f"Forced provider historical failed for {symbol}: {e}")
                    return await self._get_demo_historical(symbol, period)
            return await self._get_demo_historical(symbol, period)
        
        # AUTO / INDIANAPI mode: IndianAPI → Demo
        try:
            return await self._try_primary_historical(symbol, period)
        except Exception as e:
            logger.warning(f"Primary provider historical failed for {symbol}: {str(e)}")
            return await self._get_demo_historical(symbol, period)
    
    async def get_company_profile(self, symbol: str) -> CompanyProfile:
        """
        Get company profile with automatic fallback logic.
        """
        if self.mode == ProviderMode.DEMO:
            return await self._get_demo_profile(symbol)
        
        if self.mode in [ProviderMode.TWELVEDATA, ProviderMode.FINNHUB]:
            if self.fallback_provider:
                try:
                    return await self.fallback_provider.get_company_profile(symbol)
                except Exception as e:
                    logger.warning(f"Forced provider profile failed for {symbol}: {e}")
                    return await self._get_demo_profile(symbol)
            return await self._get_demo_profile(symbol)
        
        # AUTO / INDIANAPI mode: IndianAPI → Demo
        try:
            return await self._try_primary_profile(symbol)
        except Exception as e:
            logger.warning(f"Primary provider profile failed for {symbol}: {str(e)}")
            return await self._get_demo_profile(symbol)
    
    # Primary provider methods (IndianAPI)
    async def _try_primary_quote(self, symbol: str) -> StockQuote:
        """Try primary provider (IndianAPI) for quote"""
        if not self.primary_provider:
            raise Exception("Primary provider (IndianAPI) not available")
        return await self.primary_provider.get_stock_quote(symbol)
    
    async def _try_primary_historical(self, symbol: str, period: str) -> HistoricalData:
        """Try primary provider (IndianAPI) for historical data"""
        if not self.primary_provider:
            raise Exception("Primary provider (IndianAPI) not available")
        return await self.primary_provider.get_historical_data(symbol, period)
    
    async def _try_primary_profile(self, symbol: str) -> CompanyProfile:
        """Try primary provider (IndianAPI) for company profile"""
        if not self.primary_provider:
            raise Exception("Primary provider (IndianAPI) not available")
        return await self.primary_provider.get_company_profile(symbol)
    
    # Demo data methods
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
    
    def _create_primary_provider(self) -> Optional[BaseStockProvider]:
        """
        Create primary provider (IndianAPI).
        
        IndianAPI is the primary provider for Indian market stocks.
        Works with both FREE tier (no key) and Premium tier (with key).
        """
        if self.mode in [ProviderMode.TWELVEDATA, ProviderMode.FINNHUB]:
            # When forcing TwelveData/Finnhub, don't create IndianAPI as primary
            return None
        
        try:
            from .indianapi_provider import IndianAPIProvider
            provider = IndianAPIProvider(api_key=INDIANAPI_KEY)
            tier = "Premium" if INDIANAPI_KEY else "FREE"
            logger.info(f"Primary provider (IndianAPI {tier}) initialized")
            return provider
        except Exception as e:
            logger.error(f"Failed to initialize IndianAPI provider: {e}")
            return None
    
    def _create_fallback_provider(self) -> Optional[BaseStockProvider]:
        """
        Create fallback provider — only used when STOCK_PROVIDER is explicitly
        set to 'twelvedata' or 'finnhub'.
        
        NOT used in AUTO mode (TwelveData/Finnhub don't support Indian stocks).
        """
        if self.mode == ProviderMode.TWELVEDATA and TWELVEDATA_API_KEY:
            from .twelvedata_provider import TwelveDataProvider
            logger.info("Fallback provider (TwelveData) initialized (forced mode)")
            return TwelveDataProvider(api_key=TWELVEDATA_API_KEY)
        
        if self.mode == ProviderMode.FINNHUB and FINNHUB_API_KEY:
            from .finnhub_provider import FinnhubProvider
            logger.info("Fallback provider (Finnhub) initialized (forced mode)")
            return FinnhubProvider(api_key=FINNHUB_API_KEY)
        
        return None
    
    def get_provider_status(self) -> dict:
        """Get current provider status for debugging"""
        return {
            "mode": self.mode.value,
            "primary_available": self.primary_provider is not None,
            "fallback_available": self.fallback_provider is not None,
            "primary_provider": "IndianAPI" if self.primary_provider else None,
            "fallback_provider": (
                "TwelveData" if self.mode == ProviderMode.TWELVEDATA and self.fallback_provider
                else "Finnhub" if self.mode == ProviderMode.FINNHUB and self.fallback_provider
                else None
            )
        }