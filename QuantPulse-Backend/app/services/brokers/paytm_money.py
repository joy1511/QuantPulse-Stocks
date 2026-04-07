"""
Paytm Money API Integration
FREE API - No monthly charges
"""

from typing import List, Dict, Optional
import logging
import os
from app.services.broker_service import BrokerService

logger = logging.getLogger(__name__)


class PaytmMoneyService(BrokerService):
    """Paytm Money API integration"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: Optional[str] = None, **kwargs):
        super().__init__(api_key=api_key, api_secret=api_secret, access_token=access_token)
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.pm = None
    
    def get_login_url(self, user_id: str) -> Optional[str]:
        """Generate Paytm Money OAuth URL"""
        try:
            from pyPMClient import PMClient
            
            self.pm = PMClient(api_secret=self.api_secret, api_key=self.api_key)
            return self.pm.login(state_key=user_id)
            
        except ImportError:
            raise Exception("pyPMClient package not installed. Run: pip install pyPMClient")
        except Exception as e:
            logger.error(f"Failed to generate Paytm Money login URL: {e}")
            raise
    
    async def authenticate(self, request_token: Optional[str] = None) -> dict:
        """Authenticate with Paytm Money"""
        try:
            from pyPMClient import PMClient
            
            if not self.pm:
                self.pm = PMClient(api_secret=self.api_secret, api_key=self.api_key)
            
            if request_token:
                # Exchange request token for access token
                result = self.pm.generate_session(request_token=request_token)
                self.access_token = result.get("access_token")
                return {
                    "access_token": result.get("access_token"),
                    "public_access_token": result.get("public_access_token"),
                    "read_access_token": result.get("read_access_token")
                }
            elif self.access_token:
                # Use existing access token
                self.pm.set_access_token(self.access_token)
                return {"access_token": self.access_token}
            else:
                raise Exception("No request_token or access_token provided")
                
        except ImportError:
            raise Exception("pyPMClient package not installed. Run: pip install pyPMClient")
        except Exception as e:
            logger.error(f"Paytm Money authentication failed: {e}")
            raise
    
    async def fetch_holdings(self) -> List[Dict]:
        """Fetch holdings from Paytm Money"""
        try:
            if not self.pm or not self.access_token:
                raise Exception("Not authenticated. Call authenticate() first.")
            
            holdings = self.pm.user_holdings_data()
            
            if holdings and holdings.get('data'):
                return self._transform_holdings(holdings['data'])
            else:
                logger.warning("No holdings found in Paytm Money account")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch Paytm Money holdings: {e}")
            raise
    
    def _transform_holdings(self, raw_holdings: List[Dict]) -> List[Dict]:
        """Transform Paytm Money format to standard format"""
        return [{
            "symbol": h.get("symbol", ""),
            "exchange": h.get("exchange", "NSE"),
            "quantity": int(h.get("quantity", 0)),
            "avg_price": float(h.get("avg_price", 0)),
            "current_price": float(h.get("current_price", 0)),
            "pnl": float(h.get("pnl", 0)),
            "pnl_percentage": float(h.get("pnl_percentage", 0)),
            "broker_security_id": h.get("security_id", "")
        } for h in raw_holdings if h.get("quantity", 0) > 0]

    
    def set_tokens(self, tokens: dict):
        """Set tokens from encrypted storage"""
        try:
            from pyPMClient import PMClient
            
            if not self.pm:
                self.pm = PMClient(api_secret=self.api_secret, api_key=self.api_key)
            
            if "access_token" in tokens:
                self.access_token = tokens["access_token"]
                self.pm.set_access_token(self.access_token)
                
        except Exception as e:
            logger.error(f"Failed to set tokens: {e}")
            raise
