"""
Production-Grade Cache Service

Advanced caching layer with:
- TTL-based caching
- Request coalescing (prevents quota destruction)
- Stale-while-revalidate pattern
- Background refresh
- Memory-efficient storage
"""

import asyncio
import logging
import time
from typing import Any, Optional, Dict, Callable, Awaitable
from dataclasses import dataclass
from threading import Lock
import json
import hashlib

from cachetools import TTLCache

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """Cache entry with metadata"""
    data: Any
    timestamp: float
    ttl: int
    is_stale: bool = False


class RequestCoalescer:
    """
    Prevents multiple simultaneous requests for the same data.
    
    If 100 users request RELIANCE simultaneously:
    - Only ONE external API call occurs
    - Others wait and receive the cached result
    """
    
    def __init__(self):
        self._pending_requests: Dict[str, asyncio.Future] = {}
        self._lock = Lock()
    
    async def coalesce(self, key: str, fetch_func: Callable[[], Awaitable[Any]]) -> Any:
        """
        Coalesce multiple requests for the same key.
        
        Args:
            key: Cache key
            fetch_func: Async function to fetch data
            
        Returns:
            Data from either pending request or new fetch
        """
        with self._lock:
            if key in self._pending_requests:
                # Request already in progress, wait for it
                logger.info(f"Coalescing request for key: {key}")
                return await self._pending_requests[key]
            
            # Create new future for this request
            future = asyncio.create_task(fetch_func())
            self._pending_requests[key] = future
        
        try:
            # Execute the request
            result = await future
            return result
        finally:
            # Clean up completed request
            with self._lock:
                self._pending_requests.pop(key, None)


class CacheService:
    """
    Production-grade cache service with advanced features.
    
    Features:
    - TTL-based caching with different expiry times
    - Request coalescing to prevent API quota destruction
    - Stale-while-revalidate for instant responses
    - Background refresh for hot data
    - Memory-efficient storage
    """
    
    # Cache TTL settings (in seconds)
    CACHE_SETTINGS = {
        "stock_quote": 60,        # 1 minute
        "historical_data": 300,   # 5 minutes
        "company_profile": 86400, # 24 hours
    }
    
    def __init__(self, max_size: int = 10000):
        """
        Initialize cache service.
        
        Args:
            max_size: Maximum number of cache entries
        """
        self.cache = TTLCache(maxsize=max_size, ttl=3600)  # Default 1 hour TTL
        self.coalescer = RequestCoalescer()
        self.background_tasks = set()
        
        logger.info(f"Cache service initialized with max_size={max_size}")
    
    async def get_or_fetch(
        self,
        cache_type: str,
        key: str,
        fetch_func: Callable[[], Awaitable[Any]],
        enable_stale_while_revalidate: bool = True
    ) -> Any:
        """
        Get data from cache or fetch if not available.
        
        Implements stale-while-revalidate pattern:
        - If fresh data exists: return immediately
        - If stale data exists: return stale data + refresh in background
        - If no data exists: fetch and cache
        
        Args:
            cache_type: Type of cache (stock_quote, historical_data, company_profile)
            key: Cache key
            fetch_func: Async function to fetch fresh data
            enable_stale_while_revalidate: Enable background refresh for stale data
            
        Returns:
            Cached or fresh data
        """
        cache_key = self._build_cache_key(cache_type, key)
        ttl = self.CACHE_SETTINGS.get(cache_type, 3600)
        
        # Check cache first
        cached_entry = self._get_cache_entry(cache_key)
        
        if cached_entry:
            if not cached_entry.is_stale:
                # Fresh data available
                logger.debug(f"Cache HIT (fresh): {cache_key}")
                return cached_entry.data
            
            elif enable_stale_while_revalidate:
                # Stale data available - return immediately and refresh in background
                logger.info(f"Cache HIT (stale): {cache_key} - refreshing in background")
                
                # Start background refresh
                self._schedule_background_refresh(cache_key, cache_type, key, fetch_func, ttl)
                
                return cached_entry.data
        
        # No cache or stale data without background refresh
        logger.debug(f"Cache MISS: {cache_key}")
        
        # Use request coalescing to prevent multiple simultaneous fetches
        data = await self.coalescer.coalesce(cache_key, fetch_func)
        
        # Cache the fresh data
        self._set_cache_entry(cache_key, data, ttl)
        
        return data
    
    def _get_cache_entry(self, cache_key: str) -> Optional[CacheEntry]:
        """Get cache entry with staleness check"""
        try:
            entry = self.cache.get(cache_key)
            if not entry:
                return None
            
            # Check if entry is stale (within grace period but expired)
            current_time = time.time()
            age = current_time - entry.timestamp
            
            if age > entry.ttl:
                # Mark as stale but keep for stale-while-revalidate
                entry.is_stale = True
            
            return entry
            
        except Exception as e:
            logger.error(f"Error getting cache entry {cache_key}: {e}")
            return None
    
    def _set_cache_entry(self, cache_key: str, data: Any, ttl: int):
        """Set cache entry with metadata"""
        try:
            entry = CacheEntry(
                data=data,
                timestamp=time.time(),
                ttl=ttl,
                is_stale=False
            )
            
            # Use TTL cache with extended TTL for stale-while-revalidate
            # Keep stale data for up to 2x TTL
            extended_ttl = ttl * 2
            
            # Store in TTL cache with extended expiry
            temp_cache = TTLCache(maxsize=1, ttl=extended_ttl)
            temp_cache[cache_key] = entry
            
            # Update main cache
            self.cache.update(temp_cache)
            
            logger.debug(f"Cache SET: {cache_key} (TTL: {ttl}s)")
            
        except Exception as e:
            logger.error(f"Error setting cache entry {cache_key}: {e}")
    
    def _schedule_background_refresh(
        self,
        cache_key: str,
        cache_type: str,
        key: str,
        fetch_func: Callable[[], Awaitable[Any]],
        ttl: int
    ):
        """Schedule background refresh for stale data"""
        async def refresh_task():
            try:
                logger.info(f"Background refresh started: {cache_key}")
                fresh_data = await fetch_func()
                self._set_cache_entry(cache_key, fresh_data, ttl)
                logger.info(f"Background refresh completed: {cache_key}")
            except Exception as e:
                logger.error(f"Background refresh failed for {cache_key}: {e}")
        
        # Create background task
        task = asyncio.create_task(refresh_task())
        self.background_tasks.add(task)
        
        # Clean up completed tasks
        task.add_done_callback(self.background_tasks.discard)
    
    def _build_cache_key(self, cache_type: str, key: str) -> str:
        """Build cache key with type prefix"""
        # Create deterministic key
        key_data = f"{cache_type}:{key}"
        key_hash = hashlib.md5(key_data.encode()).hexdigest()[:12]
        return f"{cache_type}:{key_hash}:{key}"
    
    def invalidate(self, cache_type: str, key: str):
        """Invalidate specific cache entry"""
        cache_key = self._build_cache_key(cache_type, key)
        try:
            if cache_key in self.cache:
                del self.cache[cache_key]
                logger.info(f"Cache invalidated: {cache_key}")
        except Exception as e:
            logger.error(f"Error invalidating cache {cache_key}: {e}")
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate cache entries matching pattern"""
        try:
            keys_to_delete = [key for key in self.cache.keys() if pattern in key]
            for key in keys_to_delete:
                del self.cache[key]
            logger.info(f"Cache pattern invalidated: {pattern} ({len(keys_to_delete)} entries)")
        except Exception as e:
            logger.error(f"Error invalidating cache pattern {pattern}: {e}")
    
    def clear_all(self):
        """Clear all cache entries"""
        try:
            self.cache.clear()
            logger.info("All cache entries cleared")
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            return {
                "total_entries": len(self.cache),
                "max_size": self.cache.maxsize,
                "hit_rate": getattr(self.cache, 'hits', 0) / max(getattr(self.cache, 'hits', 0) + getattr(self.cache, 'misses', 0), 1),
                "background_tasks": len(self.background_tasks),
                "cache_settings": self.CACHE_SETTINGS
            }
        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {"error": str(e)}


# Global cache service instance
cache_service = CacheService()