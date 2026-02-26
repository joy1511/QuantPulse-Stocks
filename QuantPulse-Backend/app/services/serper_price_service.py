"""
Serper Price Service - Live Stock Price Fallback

Uses Serper API (Google Search) to fetch live stock prices when yfinance fails.
This is a fallback mechanism to ensure the Vercel website always has live data.
"""

import os
import logging
import httpx
import re
from typing import Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class SerperPriceService:
    """
    Service to fetch live stock prices using Serper API (Google Search).
    
    This acts as a fallback when yfinance fails to provide live data.
    """
    
    def __init__(self):
        self.api_key = os.getenv("SERPER_API_KEY")
        self.base_url = "https://google.serper.dev/search"
        
        if not self.api_key:
            logger.warning("⚠️ SERPER_API_KEY not found. Live price fallback disabled.")
    
    async def get_live_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Fetch live stock price from Moneycontrol stock quote page via Serper API.
        
        Strategy:
        1. Search for EXACT Moneycontrol stock quote page URL
        2. Only extract price from /india/stockpricequote/ pages
        3. Validate price is from the correct stock page
        
        Args:
            symbol: Stock symbol (e.g., "RELIANCE", "TCS")
            
        Returns:
            dict: Live price data or None if failed
        """
        if not self.api_key:
            logger.error("Cannot fetch live price: SERPER_API_KEY not configured")
            return None
        
        try:
            # Clean symbol
            clean_symbol = symbol.strip().upper().replace(".NS", "")
            
            # Target EXACT Moneycontrol stock quote page
            # Example: https://www.moneycontrol.com/india/stockpricequote/refineries/relianceindustries/RI
            query = f"{clean_symbol} site:moneycontrol.com/india/stockpricequote"
            
            logger.info(f"🔍 Fetching live price for {clean_symbol} from Moneycontrol stock quote page...")
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    self.base_url,
                    json={"q": query, "gl": "in", "hl": "en"},
                    headers={
                        "X-API-KEY": self.api_key,
                        "Content-Type": "application/json"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Serper API error: {response.status_code}")
                    return None
                
                data = response.json()
                
                # Extract price ONLY from stockpricequote pages
                price_data = self._extract_price_from_moneycontrol(data, clean_symbol)
                
                if price_data:
                    logger.info(f"✅ Live price fetched for {clean_symbol}: ₹{price_data['price']} (Moneycontrol)")
                    return price_data
                
                logger.warning(f"⚠️ Could not extract price for {clean_symbol} from Moneycontrol")
                return None
                    
        except Exception as e:
            logger.error(f"Error fetching live price via Serper: {e}")
            return None
    
    def _extract_price_from_moneycontrol(self, data: Dict, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Extract stock price ONLY from Moneycontrol stock quote pages.
        
        Only accepts results from:
        - moneycontrol.com/india/stockpricequote/
        
        This ensures we get the actual live stock price, not random numbers
        from news articles or other pages.
        """
        try:
            # Only check organic results
            if "organic" not in data:
                return None
            
            for result in data["organic"][:5]:  # Check first 5 results
                link = result.get("link", "")
                snippet = result.get("snippet", "")
                title = result.get("title", "")
                
                # CRITICAL: Only accept stockpricequote pages
                if "/india/stockpricequote/" not in link:
                    logger.debug(f"Skipping non-quote page: {link}")
                    continue
                
                # Verify the page is about the correct stock
                # The symbol should appear in the title or snippet
                if symbol.lower() not in title.lower() and symbol.lower() not in snippet.lower():
                    logger.debug(f"Stock name mismatch in: {title}")
                    continue
                
                logger.info(f"✅ Found Moneycontrol quote page: {link}")
                
                # Moneycontrol stock quote page patterns
                # Example snippet: "Reliance Industries Ltd. ₹ 1,234.56 +12.34 (+1.01%)"
                price_patterns = [
                    r'₹\s*([\d,]+\.?\d*)',  # ₹ 1,234.56
                    r'Rs\.?\s*([\d,]+\.?\d*)',  # Rs 1,234.56
                    r'Price[:\s]+₹?\s*([\d,]+\.?\d*)',  # Price: 1,234.56
                    r'Current Price[:\s]+₹?\s*([\d,]+\.?\d*)',  # Current Price: 1,234.56
                ]
                
                for pattern in price_patterns:
                    price_match = re.search(pattern, snippet, re.IGNORECASE)
                    if price_match:
                        try:
                            price = float(price_match.group(1).replace(',', ''))
                            
                            # Strict validation: NSE stocks are typically ₹1 - ₹100,000
                            if not (1 <= price <= 100000):
                                logger.warning(f"Price {price} out of valid range, skipping")
                                continue
                            
                            # Try to extract change and change percent
                            change = None
                            change_pct = None
                            
                            # Pattern: +12.34 (+1.01%) or -12.34 (-1.01%)
                            change_match = re.search(r'([+-]?\d+\.?\d*)\s*\(([+-]?\d+\.?\d*)%\)', snippet)
                            if change_match:
                                try:
                                    change = float(change_match.group(1))
                                    change_pct = float(change_match.group(2))
                                except ValueError:
                                    pass
                            
                            logger.info(f"✅ Extracted price ₹{price} from Moneycontrol quote page")
                            return {
                                "symbol": symbol,
                                "price": price,
                                "change": change,
                                "change_percent": change_pct,
                                "timestamp": datetime.now().isoformat(),
                                "source": "moneycontrol_stockquote",
                                "url": link
                            }
                        except (ValueError, IndexError) as e:
                            logger.debug(f"Failed to parse price: {e}")
                            continue
            
            logger.warning(f"⚠️ No valid price found in Moneycontrol stock quote pages")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting price from Moneycontrol: {e}")
            return None


# Global instance
serper_price_service = SerperPriceService()
