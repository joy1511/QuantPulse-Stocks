"""
Broker Service - Multi-broker portfolio integration

Supports: Angel One, Groww, Dhan, Paytm Money
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class BrokerService(ABC):
    """Base class for all broker integrations"""
    
    def __init__(self, **credentials):
        self.credentials = credentials
    
    @abstractmethod
    def get_login_url(self, user_id: str) -> Optional[str]:
        """Generate OAuth login URL (if applicable)"""
        pass
    
    @abstractmethod
    async def authenticate(self, request_token: Optional[str] = None) -> dict:
        """Authenticate and get access tokens"""
        pass
    
    @abstractmethod
    async def fetch_holdings(self) -> List[Dict]:
        """Fetch user's holdings from broker"""
        pass
    
    def get_broker_id(self) -> str:
        """Return broker identifier"""
        return self.__class__.__name__.replace('Service', '').lower()
    
    def _transform_to_standard_format(self, holdings: List[Dict]) -> List[Dict]:
        """Transform broker-specific format to standard format"""
        return holdings


class BrokerFactory:
    """Factory to create broker service instances"""
    
    @staticmethod
    def create_broker(broker_id: str, credentials: dict) -> BrokerService:
        """Create a broker service instance"""
        
        # Import broker implementations
        from app.services.brokers.angel_one import AngelOneService
        from app.services.brokers.groww import GrowwService
        from app.services.brokers.dhan import DhanService
        from app.services.brokers.paytm_money import PaytmMoneyService
        
        brokers = {
            "angel_one": AngelOneService,
            "groww": GrowwService,
            "dhan": DhanService,
            "paytm_money": PaytmMoneyService,
        }
        
        broker_class = brokers.get(broker_id.lower())
        if not broker_class:
            raise ValueError(f"Unsupported broker: {broker_id}")
        
        return broker_class(**credentials)
    
    @staticmethod
    def get_supported_brokers() -> List[Dict]:
        """Get list of supported brokers"""
        return [
            {
                "id": "angel_one",
                "name": "Angel One",
                "auth_type": "credentials",
                "fields_required": ["api_key", "client_code", "password", "totp_token"]
            },
            {
                "id": "groww",
                "name": "Groww",
                "auth_type": "oauth",
                "fields_required": ["api_key", "api_secret"]
            },
            {
                "id": "dhan",
                "name": "Dhan",
                "auth_type": "token",
                "fields_required": ["client_id", "access_token"]
            },
            {
                "id": "paytm_money",
                "name": "Paytm Money",
                "auth_type": "oauth",
                "fields_required": ["api_key", "api_secret"]
            }
        ]
