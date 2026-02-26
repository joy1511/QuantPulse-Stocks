"""
Stock Service

Main business logic layer that orchestrates providers, caching, and data flow.
This is the single entry point for all stock data operations.
"""

import logging
from typing import Dict, Any, Optional

from ..providers.provider_factory import ProviderFactory
from ..providers.base import StockQuote, CompanyProfile, HistoricalData
from .cache_service import cache_service

logger = logging.getLogger(__name__)


class StockService:
    """
    Main stock service that coordinates all stock data operations.
    
    Architecture:
    Router → StockService → CacheService → ProviderFactory → Providers → Demo Fallback
    
    Features:
    - Centralized business logic
    - Automatic caching with TTL
    - Provider abstraction
    - Error handling and logging
    - Demo mode support
    """
    
    def __init__(self):
        self.provider_factory = ProviderFactory()
        logger.info("Stock service initialized")
    
    async def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """
        Get current stock quote with caching.
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE")
            
        Returns:
            dict: Normalized stock quote data
        """
        try:
            # Clean and validate symbol
            clean_symbol = self._clean_symbol(symbol)
            
            # Use cache service with request coalescing
            quote = await cache_service.get_or_fetch(
                cache_type="stock_quote",
                key=clean_symbol,
                fetch_func=lambda: self.provider_factory.get_stock_quote(clean_symbol),
                enable_stale_while_revalidate=True
            )
            
            # Convert to dict for API response
            result = self._quote_to_dict(quote)
            
            # Add service metadata
            result["service_info"] = {
                "cached": True,
                "provider_status": self.provider_factory.get_provider_status()
            }
            
            logger.info(f"Stock quote served for {clean_symbol} (demo: {quote.is_demo})")
            return result
            
        except Exception as e:
            logger.error(f"Error in get_stock_quote for {symbol}: {str(e)}")
            raise
    
    async def get_historical_data(self, symbol: str, period: str = "1mo") -> Dict[str, Any]:
        """
        Get historical stock data with caching.
        
        Args:
            symbol: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            
        Returns:
            dict: Normalized historical data
        """
        try:
            clean_symbol = self._clean_symbol(symbol)
            cache_key = f"{clean_symbol}_{period}"
            
            # Use cache service
            historical = await cache_service.get_or_fetch(
                cache_type="historical_data",
                key=cache_key,
                fetch_func=lambda: self.provider_factory.get_historical_data(clean_symbol, period),
                enable_stale_while_revalidate=True
            )
            
            # Convert to dict for API response
            result = self._historical_to_dict(historical)
            
            # Add service metadata
            result["service_info"] = {
                "cached": True,
                "provider_status": self.provider_factory.get_provider_status()
            }
            
            logger.info(f"Historical data served for {clean_symbol} ({period}) (demo: {historical.is_demo})")
            return result
            
        except Exception as e:
            logger.error(f"Error in get_historical_data for {symbol}: {str(e)}")
            raise
    
    async def get_company_profile(self, symbol: str) -> Dict[str, Any]:
        """
        Get company profile with caching.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            dict: Normalized company profile data
        """
        try:
            clean_symbol = self._clean_symbol(symbol)
            
            # Use cache service
            profile = await cache_service.get_or_fetch(
                cache_type="company_profile",
                key=clean_symbol,
                fetch_func=lambda: self.provider_factory.get_company_profile(clean_symbol),
                enable_stale_while_revalidate=True
            )
            
            # Convert to dict for API response
            result = self._profile_to_dict(profile)
            
            # Add service metadata
            result["service_info"] = {
                "cached": True,
                "provider_status": self.provider_factory.get_provider_status()
            }
            
            logger.info(f"Company profile served for {clean_symbol} (demo: {profile.is_demo})")
            return result
            
        except Exception as e:
            logger.error(f"Error in get_company_profile for {symbol}: {str(e)}")
            raise
    
    async def get_multiple_quotes(self, symbols: list[str]) -> Dict[str, Any]:
        """
        Get multiple stock quotes efficiently.
        
        Args:
            symbols: List of stock symbols
            
        Returns:
            dict: Multiple stock quotes
        """
        try:
            results = {}
            errors = {}
            
            # Process all symbols concurrently
            import asyncio
            
            async def get_single_quote(symbol: str):
                try:
                    return symbol, await self.get_stock_quote(symbol)
                except Exception as e:
                    return symbol, {"error": str(e)}
            
            # Execute all requests concurrently
            tasks = [get_single_quote(symbol) for symbol in symbols]
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process responses
            for response in responses:
                if isinstance(response, Exception):
                    continue
                
                symbol, data = response
                if "error" in data:
                    errors[symbol] = data["error"]
                else:
                    results[symbol] = data
            
            return {
                "quotes": results,
                "errors": errors,
                "total_requested": len(symbols),
                "successful": len(results),
                "failed": len(errors)
            }
            
        except Exception as e:
            logger.error(f"Error in get_multiple_quotes: {str(e)}")
            raise
    
    def invalidate_cache(self, symbol: Optional[str] = None):
        """
        Invalidate cache for specific symbol or all data.
        
        Args:
            symbol: Stock symbol to invalidate (None for all)
        """
        try:
            if symbol:
                clean_symbol = self._clean_symbol(symbol)
                cache_service.invalidate("stock_quote", clean_symbol)
                cache_service.invalidate_pattern(clean_symbol)  # Invalidate historical data too
                logger.info(f"Cache invalidated for {clean_symbol}")
            else:
                cache_service.clear_all()
                logger.info("All cache invalidated")
        except Exception as e:
            logger.error(f"Error invalidating cache: {str(e)}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """
        Get comprehensive service status.
        
        Returns:
            dict: Service status information
        """
        try:
            return {
                "service": "StockService",
                "status": "operational",
                "provider_status": self.provider_factory.get_provider_status(),
                "cache_stats": cache_service.get_stats(),
                "supported_periods": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"]
            }
        except Exception as e:
            logger.error(f"Error getting service status: {str(e)}")
            return {"service": "StockService", "status": "error", "error": str(e)}
    
    # Helper methods
    def _clean_symbol(self, symbol: str) -> str:
        """Clean and validate stock symbol"""
        if not symbol:
            raise ValueError("Symbol cannot be empty")
        
        # Remove whitespace and convert to uppercase
        clean = symbol.strip().upper()
        
        # Remove any existing suffixes
        if clean.endswith(".NS") or clean.endswith(".BO"):
            clean = clean[:-3]
        
        # Basic validation
        if not clean.isalnum():
            raise ValueError(f"Invalid symbol format: {symbol}")
        
        return clean
    
    def _quote_to_dict(self, quote: StockQuote) -> Dict[str, Any]:
        """Convert StockQuote to dictionary"""
        return {
            "symbol": quote.symbol,
            "companyName": quote.symbol,  # Will be enhanced with real company names
            "currentPrice": quote.price,
            "previousClose": quote.previous_close,
            "change": quote.change,
            "changePercent": quote.percent_change,
            "volume": quote.volume,
            "volumeFormatted": self._format_volume(quote.volume),
            "currency": quote.currency,
            "exchange": quote.exchange,
            "timestamp": quote.timestamp,
            "marketState": quote.market_state,
            "isDemoData": quote.is_demo
        }
    
    def _historical_to_dict(self, historical: HistoricalData) -> Dict[str, Any]:
        """Convert HistoricalData to dictionary"""
        return {
            "symbol": historical.symbol,
            "period": historical.period,
            "data": historical.data,
            "dataPoints": len(historical.data),
            "isDemoData": historical.is_demo
        }
    
    def _profile_to_dict(self, profile: CompanyProfile) -> Dict[str, Any]:
        """Convert CompanyProfile to dictionary"""
        return {
            "symbol": profile.symbol,
            "name": profile.name,
            "description": profile.description,
            "sector": profile.sector,
            "industry": profile.industry,
            "marketCap": profile.market_cap,
            "marketCapFormatted": profile.market_cap_formatted,
            "employees": profile.employees,
            "website": profile.website,
            "isDemoData": profile.is_demo
        }
    
    def _format_volume(self, volume: int) -> str:
        """Format trading volume"""
        if volume >= 1e6:
            return f"{volume / 1e6:.2f}M"
        elif volume >= 1e3:
            return f"{volume / 1e3:.1f}K"
        else:
            return str(volume)


# Global stock service instance
stock_service = StockService()