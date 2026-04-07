"""
Angel One SmartAPI Integration
FREE API - No monthly charges
"""

from typing import List, Dict, Optional
import logging
from app.services.broker_service import BrokerService

logger = logging.getLogger(__name__)


class AngelOneService(BrokerService):
    """Angel One SmartAPI integration"""
    
    def __init__(self, api_key: str, client_code: str, password: str, totp_token: str, **kwargs):
        super().__init__(api_key=api_key, client_code=client_code, password=password, totp_token=totp_token)
        self.api_key = api_key
        self.client_code = client_code
        self.password = password
        self.totp_token = totp_token
        self.smart_api = None
    
    def get_login_url(self, user_id: str) -> Optional[str]:
        """Angel One uses direct login, no OAuth URL"""
        return None
    
    async def authenticate(self, request_token: Optional[str] = None) -> dict:
        """Authenticate with Angel One"""
        try:
            from SmartApi import SmartConnect
            
            self.smart_api = SmartConnect(api_key=self.api_key)
            
            # Generate session
            data = self.smart_api.generateSession(
                self.client_code,
                self.password,
                self.totp_token
            )
            
            if data['status']:
                return {
                    "access_token": data['data']['jwtToken'],
                    "refresh_token": data['data']['refreshToken'],
                    "feed_token": data['data']['feedToken']
                }
            else:
                raise Exception(f"Authentication failed: {data.get('message', 'Unknown error')}")
                
        except ImportError:
            raise Exception("SmartApi package not installed. Run: pip install smartapi-python")
        except Exception as e:
            logger.error(f"Angel One authentication failed: {e}")
            raise
    
    async def fetch_holdings(self) -> List[Dict]:
        """Fetch holdings from Angel One"""
        try:
            if not self.smart_api:
                raise Exception("Not authenticated. Call authenticate() first.")
            
            response = self.smart_api.holding()
            
            if response['status'] and response['data']:
                return self._transform_holdings(response['data'])
            else:
                logger.warning(f"No holdings found or error: {response.get('message')}")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch Angel One holdings: {e}")
            raise
    
    def _transform_holdings(self, raw_holdings: List[Dict]) -> List[Dict]:
        """Transform Angel One format to standard format"""
        return [{
            "symbol": h.get("tradingsymbol", ""),
            "exchange": h.get("exchange", "NSE"),
            "quantity": int(h.get("quantity", 0)),
            "avg_price": float(h.get("averageprice", 0)),
            "current_price": float(h.get("ltp", 0)),
            "pnl": float(h.get("pnl", 0)),
            "pnl_percentage": float(h.get("pnlpercentage", 0)),
            "broker_security_id": h.get("symboltoken", "")
        } for h in raw_holdings if h.get("quantity", 0) > 0]

    
    def set_tokens(self, tokens: dict):
        """Set tokens from encrypted storage"""
        try:
            from SmartApi import SmartConnect
            
            if not self.smart_api:
                self.smart_api = SmartConnect(api_key=self.api_key)
            
            # Set the access token
            if "access_token" in tokens:
                self.smart_api.setAccessToken(tokens["access_token"])
            
            if "feed_token" in tokens:
                self.smart_api.feed_token = tokens["feed_token"]
                
        except Exception as e:
            logger.error(f"Failed to set tokens: {e}")
            raise
