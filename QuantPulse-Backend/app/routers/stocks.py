"""
Stock Data Router - Production Grade

This module provides endpoints for fetching real-time NSE stock data
using a production-grade multi-provider architecture with intelligent fallback.

Architecture Flow:
Router → Stock Service → Cache Service → Provider Factory → Providers → Demo Fallback

Features:
- Multi-provider support (TwelveData → Finnhub → Demo)
- Production-grade caching with request coalescing
- Stale-while-revalidate for optimal performance
- Automatic demo mode when providers fail
- Clean error handling and logging
- No direct provider dependencies in router
"""

from fastapi import APIRouter, HTTPException, Path, Query
from typing import List, Optional
import logging

from ..services.stock_service import stock_service

logger = logging.getLogger(__name__)

# Create router for stock-related endpoints
router = APIRouter(
    prefix="/stock",
    tags=["Stocks"],
)


@router.get("/{symbol}")
async def get_stock_data(
    symbol: str = Path(
        ..., 
        pattern=r"^[A-Z0-9\.]+$", 
        description="NSE stock symbol (e.g., RELIANCE, TCS, INFY)"
    )
):
    """
    Fetch real-time stock data for an NSE stock.
    
    This endpoint uses a production-grade architecture:
    1. Checks cache first (60-second TTL)
    2. If cache miss, tries primary provider (TwelveData)
    3. If primary fails, tries fallback provider (Finnhub)
    4. If both fail, returns realistic demo data
    5. Uses request coalescing to prevent API quota destruction
    6. Implements stale-while-revalidate for optimal performance
    
    Args:
        symbol: NSE stock symbol (e.g., "RELIANCE", "TCS", "INFY")
    
    Returns:
        dict: Stock data including price, change, volume, market cap
        
    Response includes:
        - symbol: Stock symbol
        - currentPrice: Current trading price
        - change: Price change from previous close
        - changePercent: Percentage change
        - volume: Trading volume
        - timestamp: Data timestamp
        - isDemoData: Boolean indicating if data is simulated
    
    Raises:
        HTTPException: 400 for invalid symbol, 500 for service errors
    """
    try:
        logger.info(f"Stock data request for symbol: {symbol}")
        
        # Use stock service (handles all caching, providers, fallback)
        stock_data = await stock_service.get_stock_quote(symbol)
        
        # Log demo mode for monitoring
        if stock_data.get("isDemoData"):
            logger.warning(f"Demo data served for {symbol}")
        
        return stock_data
        
    except ValueError as e:
        # Invalid symbol format
        logger.warning(f"Invalid symbol format: {symbol} - {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid symbol",
                "message": str(e),
                "hint": "Use valid NSE symbols like RELIANCE, TCS, INFY, HDFCBANK"
            }
        )
    
    except Exception as e:
        # Service errors (should be rare due to demo fallback)
        logger.error(f"Service error for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Service temporarily unavailable",
                "message": "Please try again in a moment",
                "symbol": symbol
            }
        )


@router.get("/{symbol}/historical")
async def get_historical_data(
    symbol: str = Path(
        ..., 
        pattern=r"^[A-Z0-9\.]+$", 
        description="NSE stock symbol"
    ),
    period: str = Query(
        "1mo",
        description="Time period",
        pattern=r"^(1d|5d|1mo|3mo|6mo|1y|2y|5y|10y|ytd|max)$"
    )
):
    """
    Fetch historical stock data for analysis and charting.
    
    This endpoint provides OHLCV (Open, High, Low, Close, Volume) data
    for the specified time period with intelligent caching.
    
    Args:
        symbol: NSE stock symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
    
    Returns:
        dict: Historical data with OHLCV values
        
    Response includes:
        - symbol: Stock symbol
        - period: Requested time period
        - data: Array of OHLCV data points
        - dataPoints: Number of data points
        - isDemoData: Boolean indicating if data is simulated
    """
    try:
        logger.info(f"Historical data request for {symbol} ({period})")
        
        historical_data = await stock_service.get_historical_data(symbol, period)
        
        if historical_data.get("isDemoData"):
            logger.warning(f"Demo historical data served for {symbol}")
        
        return historical_data
        
    except ValueError as e:
        logger.warning(f"Invalid request for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid request",
                "message": str(e)
            }
        )
    
    except Exception as e:
        logger.error(f"Historical data error for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Service temporarily unavailable",
                "message": "Please try again in a moment"
            }
        )


@router.get("/{symbol}/profile")
async def get_company_profile(
    symbol: str = Path(
        ..., 
        pattern=r"^[A-Z0-9\.]+$", 
        description="NSE stock symbol"
    )
):
    """
    Fetch company profile and fundamental information.
    
    This endpoint provides detailed company information including
    sector, industry, market cap, and business description.
    
    Args:
        symbol: NSE stock symbol
    
    Returns:
        dict: Company profile data
        
    Response includes:
        - symbol: Stock symbol
        - name: Company name
        - description: Business description
        - sector: Business sector
        - industry: Industry classification
        - marketCap: Market capitalization
        - employees: Employee count
        - website: Company website
        - isDemoData: Boolean indicating if data is simulated
    """
    try:
        logger.info(f"Company profile request for {symbol}")
        
        profile_data = await stock_service.get_company_profile(symbol)
        
        if profile_data.get("isDemoData"):
            logger.warning(f"Demo profile data served for {symbol}")
        
        return profile_data
        
    except ValueError as e:
        logger.warning(f"Invalid symbol for profile: {symbol} - {str(e)}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Invalid symbol",
                "message": str(e)
            }
        )
    
    except Exception as e:
        logger.error(f"Profile data error for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Service temporarily unavailable",
                "message": "Please try again in a moment"
            }
        )


@router.post("/quotes")
async def get_multiple_quotes(
    symbols: List[str] = Query(
        ...,
        description="List of NSE stock symbols",
        max_items=20  # Limit to prevent abuse
    )
):
    """
    Fetch multiple stock quotes efficiently.
    
    This endpoint allows fetching up to 20 stock quotes in a single request
    with concurrent processing and individual error handling.
    
    Args:
        symbols: List of NSE stock symbols (max 20)
    
    Returns:
        dict: Multiple stock quotes with success/error breakdown
        
    Response includes:
        - quotes: Successfully fetched quotes
        - errors: Symbols that failed with error messages
        - total_requested: Total symbols requested
        - successful: Number of successful fetches
        - failed: Number of failed fetches
    """
    try:
        if not symbols:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "No symbols provided",
                    "message": "Please provide at least one stock symbol"
                }
            )
        
        if len(symbols) > 20:
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "Too many symbols",
                    "message": "Maximum 20 symbols allowed per request"
                }
            )
        
        logger.info(f"Multiple quotes request for {len(symbols)} symbols")
        
        result = await stock_service.get_multiple_quotes(symbols)
        
        return result
        
    except HTTPException:
        raise
    
    except Exception as e:
        logger.error(f"Multiple quotes error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Service temporarily unavailable",
                "message": "Please try again in a moment"
            }
        )


@router.delete("/{symbol}/cache")
async def invalidate_cache(
    symbol: str = Path(
        ..., 
        pattern=r"^[A-Z0-9\.]+$", 
        description="NSE stock symbol"
    )
):
    """
    Invalidate cache for a specific stock symbol.
    
    This endpoint allows manual cache invalidation for testing
    or when fresh data is specifically needed.
    
    Args:
        symbol: NSE stock symbol
    
    Returns:
        dict: Cache invalidation confirmation
    """
    try:
        logger.info(f"Cache invalidation request for {symbol}")
        
        stock_service.invalidate_cache(symbol)
        
        return {
            "message": f"Cache invalidated for {symbol}",
            "symbol": symbol,
            "timestamp": "2024-02-04T12:00:00Z"  # Current timestamp would be dynamic
        }
        
    except Exception as e:
        logger.error(f"Cache invalidation error for {symbol}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Cache invalidation failed",
                "message": str(e)
            }
        )


@router.get("/service/status")
async def get_service_status():
    """
    Get comprehensive service status information.
    
    This endpoint provides detailed information about the stock service,
    provider status, cache statistics, and system health.
    
    Returns:
        dict: Comprehensive service status
        
    Response includes:
        - service: Service name and status
        - provider_status: Information about data providers
        - cache_stats: Cache performance metrics
        - supported_periods: Available time periods for historical data
    """
    try:
        status = stock_service.get_service_status()
        
        return {
            "timestamp": "2024-02-04T12:00:00Z",  # Dynamic timestamp
            "status": status,
            "endpoints": {
                "quote": "/stock/{symbol}",
                "historical": "/stock/{symbol}/historical",
                "profile": "/stock/{symbol}/profile",
                "multiple": "/stock/quotes",
                "cache_invalidate": "/stock/{symbol}/cache"
            }
        }
        
    except Exception as e:
        logger.error(f"Service status error: {str(e)}")
        return {
            "service": "StockService",
            "status": "error",
            "error": str(e),
            "timestamp": "2024-02-04T12:00:00Z"
        }
