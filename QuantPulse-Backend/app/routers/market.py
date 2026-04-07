"""
Market Data Router

Provides market-wide endpoints like trending stocks (top gainers/losers).
Data sourced from IndianAPI with server-side caching.
"""

import asyncio
import logging
import time
from typing import Optional
from fastapi import APIRouter, HTTPException
import httpx

from ..config import INDIANAPI_KEY

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/market",
    tags=["Market"],
)

# ── Simple In-Memory Cache ──────────────────────────────────────────
_trending_cache: dict = {"data": None, "timestamp": 0}
TRENDING_CACHE_TTL = 300  # 5 minutes (increased from 3 to reduce API calls)


async def _fetch_trending_from_indianapi() -> dict:
    """Fetch trending stocks (top gainers + losers) from IndianAPI."""
    headers = {"Content-Type": "application/json", "User-Agent": "QuantPulse/2.0"}
    if INDIANAPI_KEY:
        headers["X-API-Key"] = INDIANAPI_KEY

    # Increased timeout for trending endpoint (can be slow on free tier)
    # Use retry logic to handle transient failures
    max_retries = 2
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.get(
                    "https://stock.indianapi.in/trending",
                    headers=headers,
                )
                response.raise_for_status()
                return response.json()
        except (httpx.ConnectTimeout, httpx.ReadTimeout) as e:
            if attempt < max_retries - 1:
                logger.warning(f"⚠️ Trending API timeout (attempt {attempt + 1}/{max_retries}), retrying...")
                await asyncio.sleep(2)  # Wait 2s before retry
                continue
            raise  # Re-raise on final attempt


def _normalize_stock(raw: dict) -> dict:
    """Normalize a single stock entry from the IndianAPI response."""
    def safe_float(val, default=0.0):
        if val is None:
            return default
        try:
            return float(str(val).replace(",", ""))
        except (ValueError, TypeError):
            return default

    return {
        "ticker": raw.get("ticker_id", raw.get("ticker", "")),
        "company": raw.get("company_name", raw.get("company", "")),
        "price": safe_float(raw.get("price")),
        "percent_change": safe_float(raw.get("percent_change")),
        "net_change": safe_float(raw.get("net_change")),
        "volume": safe_float(raw.get("volume")),
        "high": safe_float(raw.get("high")),
        "low": safe_float(raw.get("low")),
        "open": safe_float(raw.get("open")),
    }


@router.get("/trending")
async def get_trending_stocks():
    """
    Get today's top gainers and losers from NSE.

    Returns top 5 gainers and top 5 losers with price, % change, volume.
    Data is cached for 3 minutes server-side.
    """
    global _trending_cache

    # Check cache
    now = time.time()
    if _trending_cache["data"] and (now - _trending_cache["timestamp"]) < TRENDING_CACHE_TTL:
        logger.debug("Trending stocks served from cache")
        return _trending_cache["data"]

    try:
        logger.info("📥 Fetching trending stocks from IndianAPI...")
        raw = await _fetch_trending_from_indianapi()

        trending = raw.get("trending_stocks", raw)

        top_gainers_raw = trending.get("top_gainers", [])
        top_losers_raw = trending.get("top_losers", [])

        # Normalize and limit to 5
        top_gainers = [_normalize_stock(s) for s in top_gainers_raw[:5]]
        top_losers = [_normalize_stock(s) for s in top_losers_raw[:5]]

        result = {
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "timestamp": now,
            "cached": False,
        }

        # Update cache
        _trending_cache = {"data": {**result, "cached": True}, "timestamp": now}

        logger.info(f"✅ Trending stocks: {len(top_gainers)} gainers, {len(top_losers)} losers")
        return result

    except httpx.HTTPStatusError as e:
        error_body = ""
        try:
            error_body = e.response.text
        except:
            pass
        logger.error(f"❌ IndianAPI trending HTTP error: {e.response.status_code} - {error_body}")
        raise HTTPException(status_code=502, detail="Failed to fetch trending stocks from data provider")

    except Exception as e:
        logger.error(f"❌ Trending stocks fetch failed: {type(e).__name__}: {str(e)}")
        # Return stale cache if available
        if _trending_cache["data"]:
            logger.warning("⚠️ Returning stale trending cache")
            return _trending_cache["data"]
        raise HTTPException(status_code=503, detail="Trending stocks temporarily unavailable")
