"""
Groww API Integration
FREE API - No monthly charges
Note: Uses direct HTTP API calls as growwapi package is not available on PyPI
"""

from typing import List, Dict, Optional
import logging
import os
import httpx
from app.services.broker_service import BrokerService

logger = logging.getLogger(__name__)


class GrowwService(BrokerService):
    """Groww API integration using direct HTTP calls"""
    
    BASE_URL = "https://api.groww.in"
    
    def __init__(self, api_key: str, api_secret: str, access_token: Optional[str] = None, **kwargs):
        super().__init__(api_key=api_key, api_secret=api_secret, access_token=access_token)
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
    
    def get_login_url(self, user_id: str) -> Optional[str]:
        """Generate Groww OAuth URL"""
        try:
            callback_url = f"{os.getenv('BACKEND_URL', 'http://localhost:8000')}/api/broker/callback?broker=groww&state={user_id}"
            
            # Groww OAuth URL format
            login_url = (
                f"{self.BASE_URL}/v1/api/login/oauth2/authorize"
                f"?api_key={self.api_key}"
                f"&redirect_uri={callback_url}"
                f"&response_type=code"
                f"&state={user_id}"
            )
            
            return login_url
            
        except Exception as e:
            logger.error(f"Failed to generate Groww login URL: {e}")
            raise
    
    async def authenticate(self, request_token: Optional[str] = None) -> dict:
        """Authenticate with Groww"""
        try:
            if request_token:
                # Exchange request token for access token
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        f"{self.BASE_URL}/v1/api/login/oauth2/token",
                        data={
                            "api_key": self.api_key,
                            "api_secret": self.api_secret,
                            "request_token": request_token,
                            "grant_type": "authorization_code"
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    self.access_token = data.get("access_token")
                    return {
                        "access_token": data.get("access_token"),
                        "refresh_token": data.get("refresh_token")
                    }
            elif self.access_token:
                # Use existing access token
                return {"access_token": self.access_token}
            else:
                raise Exception("No request_token or access_token provided")
                
        except Exception as e:
            logger.error(f"Groww authentication failed: {e}")
            raise
    
    async def fetch_holdings(self) -> List[Dict]:
        """Fetch holdings from Groww"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated. Call authenticate() first.")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.BASE_URL}/v1/api/portfolio/holdings",
                    headers={
                        "Authorization": f"Bearer {self.access_token}",
                        "X-API-Key": self.api_key
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            if data and data.get('data'):
                return self._transform_holdings(data['data'])
            else:
                logger.warning("No holdings found in Groww account")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch Groww holdings: {e}")
            raise
    
    def _transform_holdings(self, raw_holdings: List[Dict]) -> List[Dict]:
        """Transform Groww format to standard format"""
        return [{
            "symbol": h.get("tradingSymbol", ""),
            "exchange": h.get("exchange", "NSE"),
            "quantity": int(h.get("quantity", 0)),
            "avg_price": float(h.get("averagePrice", 0)),
            "current_price": float(h.get("lastPrice", 0)),
            "pnl": float(h.get("pnl", 0)),
            "pnl_percentage": float(h.get("pnlPercentage", 0)),
            "broker_security_id": h.get("securityId", "")
        } for h in raw_holdings if h.get("quantity", 0) > 0]
    
    def set_tokens(self, tokens: dict):
        """Set tokens from encrypted storage"""
        self.access_token = tokens.get("access_token")
