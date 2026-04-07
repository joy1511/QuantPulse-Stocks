"""
Dhan API Integration
FREE API - No monthly charges
"""

from typing import List, Dict, Optional
import logging
from app.services.broker_service import BrokerService

logger = logging.getLogger(__name__)


class DhanService(BrokerService):
    """Dhan API integration"""
    
    def __init__(self, client_id: str, access_token: str, **kwargs):
        super().__init__(client_id=client_id, access_token=access_token)
        self.client_id = client_id
        self.access_token = access_token
        self.dhan = None
    
    def get_login_url(self, user_id: str) -> Optional[str]:
        """Dhan uses access token, no OAuth URL"""
        return None
    
    async def authenticate(self, request_token: Optional[str] = None) -> dict:
        """Authenticate with Dhan"""
        try:
            from dhanhq import dhanhq
            
            self.dhan = dhanhq(self.client_id, self.access_token)
            return {"access_token": self.access_token}
                
        except ImportError:
            raise Exception("dhanhq package not installed. Run: pip install dhanhq")
        except Exception as e:
            logger.error(f"Dhan authentication failed: {e}")
            raise
    
    async def fetch_holdings(self) -> List[Dict]:
        """Fetch holdings from Dhan"""
        try:
            if not self.dhan:
                raise Exception("Not authenticated. Call authenticate() first.")
            
            response = self.dhan.get_holdings()
            
            if response and response.get('data'):
                return self._transform_holdings(response['data'])
            else:
                logger.warning("No holdings found in Dhan account")
                return []
                
        except Exception as e:
            logger.error(f"Failed to fetch Dhan holdings: {e}")
            raise
    
    def _transform_holdings(self, raw_holdings: List[Dict]) -> List[Dict]:
        """Transform Dhan format to standard format"""
        return [{
            "symbol": h.get("tradingSymbol", ""),
            "exchange": h.get("exchange", "NSE"),
            "quantity": int(h.get("quantity", 0)),
            "avg_price": float(h.get("avgCostPrice", 0)),
            "current_price": float(h.get("lastTradedPrice", 0)),
            "pnl": float(h.get("realizedProfit", 0)),
            "pnl_percentage": (float(h.get("realizedProfit", 0)) / (float(h.get("avgCostPrice", 1)) * int(h.get("quantity", 1))) * 100) if h.get("quantity", 0) > 0 else 0,
            "broker_security_id": h.get("securityId", "")
        } for h in raw_holdings if h.get("quantity", 0) > 0]

    
    def set_tokens(self, tokens: dict):
        """Set tokens from encrypted storage"""
        try:
            from dhanhq import dhanhq
            
            if "access_token" in tokens:
                self.access_token = tokens["access_token"]
                self.dhan = dhanhq(self.client_id, self.access_token)
                
        except Exception as e:
            logger.error(f"Failed to set tokens: {e}")
            raise
