"""
Broker Integration Router

Handles broker connection, OAuth, portfolio sync, and disconnection.
Supports: Angel One, Groww, Dhan, Paytm Money
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import logging
import os

from app.mongodb import get_collection
from app.services.auth_service import get_current_user
from app.services.broker_service import BrokerFactory
from app.utils.encryption import token_encryption

router = APIRouter(prefix="/api/broker", tags=["Broker Integration"])
logger = logging.getLogger(__name__)


# =============================================================================
# Schemas
# =============================================================================

class BrokerConnectRequest(BaseModel):
    broker_id: str = Field(..., description="Broker ID: angel_one, groww, dhan, paytm_money")
    credentials: Dict[str, str] = Field(..., description="Broker-specific credentials")


class BrokerConnectResponse(BaseModel):
    status: str
    broker: str
    login_url: Optional[str] = None
    message: str


class BrokerSyncRequest(BaseModel):
    broker_id: Optional[str] = Field(None, description="Specific broker to sync, or None for all")


class HoldingResponse(BaseModel):
    symbol: str
    exchange: str
    quantity: int
    avg_price: float
    current_price: float
    pnl: float
    pnl_percentage: float
    source: str


class BrokerSyncResponse(BaseModel):
    status: str
    broker: str
    holdings: List[HoldingResponse]
    last_synced: str
    total_holdings: int


class BrokerStatusResponse(BaseModel):
    connected_brokers: List[Dict]
    total_holdings: int


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/supported")
async def get_supported_brokers():
    """Get list of supported brokers"""
    return {
        "brokers": BrokerFactory.get_supported_brokers()
    }


@router.post("/connect", response_model=BrokerConnectResponse)
async def connect_broker(
    request: BrokerConnectRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Connect a broker account
    
    Step 1: User provides broker credentials
    Step 2: System generates OAuth URL (if needed) or authenticates directly
    Step 3: User completes OAuth flow (if needed)
    """
    try:
        broker_connections = get_collection("broker_connections")
        if not broker_connections:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Check if already connected
        existing = await broker_connections.find_one({
            "user_id": str(current_user["_id"]),
            "broker": request.broker_id
        })
        
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"{request.broker_id} is already connected. Disconnect first to reconnect."
            )
        
        # Create broker service
        broker_service = BrokerFactory.create_broker(request.broker_id, request.credentials)
        
        # Get login URL (for OAuth brokers)
        login_url = broker_service.get_login_url(str(current_user["_id"]))
        
        # Encrypt and save credentials temporarily
        encrypted_creds = {
            key: token_encryption.encrypt(value) 
            for key, value in request.credentials.items()
        }
        
        await broker_connections.insert_one({
            "user_id": str(current_user["_id"]),
            "broker": request.broker_id,
            "credentials_encrypted": encrypted_creds,
            "status": "pending" if login_url else "authenticating",
            "connected_at": datetime.utcnow()
        })
        
        # If no OAuth needed, authenticate directly
        if not login_url:
            try:
                tokens = await broker_service.authenticate()
                
                # Update with tokens
                encrypted_tokens = {
                    key: token_encryption.encrypt(str(value))
                    for key, value in tokens.items()
                }
                
                await broker_connections.update_one(
                    {"user_id": str(current_user["_id"]), "broker": request.broker_id},
                    {"$set": {
                        "tokens_encrypted": encrypted_tokens,
                        "status": "active",
                        "last_synced_at": datetime.utcnow()
                    }}
                )
                
                # Fetch holdings immediately
                holdings = await broker_service.fetch_holdings()
                await _save_holdings(str(current_user["_id"]), request.broker_id, holdings)
                
                return {
                    "status": "success",
                    "broker": request.broker_id,
                    "login_url": None,
                    "message": f"Successfully connected to {request.broker_id}. {len(holdings)} holdings synced."
                }
            except Exception as e:
                logger.error(f"Direct authentication failed: {e}")
                await broker_connections.delete_one({
                    "user_id": str(current_user["_id"]),
                    "broker": request.broker_id
                })
                raise HTTPException(status_code=400, detail=f"Authentication failed: {str(e)}")
        
        return {
            "status": "success",
            "broker": request.broker_id,
            "login_url": login_url,
            "message": f"Please complete login on {request.broker_id}"
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Connect broker failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to connect broker: {str(e)}")


@router.get("/callback")
async def broker_callback(
    request_token: str = Query(...),
    state: str = Query(...),  # user_id
    broker: str = Query(...)
):
    """
    OAuth callback endpoint
    
    Called by broker after user completes OAuth login
    """
    try:
        broker_connections = get_collection("broker_connections")
        if not broker_connections:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Find pending connection
        connection = await broker_connections.find_one({
            "user_id": state,
            "broker": broker,
            "status": "pending"
        })
        
        if not connection:
            raise HTTPException(status_code=404, detail="Connection not found or already completed")
        
        # Decrypt credentials
        decrypted_creds = {
            key: token_encryption.decrypt(value)
            for key, value in connection["credentials_encrypted"].items()
        }
        
        # Create broker service and authenticate
        broker_service = BrokerFactory.create_broker(broker, decrypted_creds)
        tokens = await broker_service.authenticate(request_token=request_token)
        
        # Encrypt and save tokens
        encrypted_tokens = {
            key: token_encryption.encrypt(str(value))
            for key, value in tokens.items()
        }
        
        await broker_connections.update_one(
            {"_id": connection["_id"]},
            {"$set": {
                "tokens_encrypted": encrypted_tokens,
                "status": "active",
                "last_synced_at": datetime.utcnow()
            }}
        )
        
        # Fetch holdings
        holdings = await broker_service.fetch_holdings()
        await _save_holdings(state, broker, holdings)
        
        # Redirect to frontend
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return RedirectResponse(
            url=f"{frontend_url}/portfolio?status=connected&broker={broker}&holdings={len(holdings)}"
        )
        
    except Exception as e:
        logger.error(f"OAuth callback failed: {e}")
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        return RedirectResponse(
            url=f"{frontend_url}/portfolio?status=error&message={str(e)}"
        )


@router.post("/sync", response_model=BrokerSyncResponse)
async def sync_broker_portfolio(
    request: BrokerSyncRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Sync portfolio from connected broker(s)
    
    If broker_id is provided, sync only that broker.
    If broker_id is None, sync all connected brokers.
    """
    try:
        broker_connections = get_collection("broker_connections")
        if not broker_connections:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Find active connections
        query = {
            "user_id": str(current_user["_id"]),
            "status": "active"
        }
        if request.broker_id:
            query["broker"] = request.broker_id
        
        connections = await broker_connections.find(query).to_list(length=100)
        
        if not connections:
            raise HTTPException(
                status_code=404,
                detail="No active broker connections found"
            )
        
        all_holdings = []
        synced_brokers = []
        
        for connection in connections:
            try:
                # Decrypt credentials and tokens
                decrypted_creds = {
                    key: token_encryption.decrypt(value)
                    for key, value in connection["credentials_encrypted"].items()
                }
                
                # Create broker service
                broker_service = BrokerFactory.create_broker(
                    connection["broker"],
                    decrypted_creds
                )
                
                # If tokens exist, set them
                if "tokens_encrypted" in connection:
                    decrypted_tokens = {
                        key: token_encryption.decrypt(value)
                        for key, value in connection["tokens_encrypted"].items()
                    }
                    # Set tokens on broker service (implementation specific)
                    if hasattr(broker_service, 'set_tokens'):
                        broker_service.set_tokens(decrypted_tokens)
                
                # Fetch holdings
                holdings = await broker_service.fetch_holdings()
                
                # Save holdings
                await _save_holdings(
                    str(current_user["_id"]),
                    connection["broker"],
                    holdings
                )
                
                all_holdings.extend(holdings)
                synced_brokers.append(connection["broker"])
                
                # Update last synced time
                await broker_connections.update_one(
                    {"_id": connection["_id"]},
                    {"$set": {"last_synced_at": datetime.utcnow()}}
                )
                
            except Exception as e:
                logger.error(f"Failed to sync {connection['broker']}: {e}")
                # Continue with other brokers
                continue
        
        if not all_holdings:
            raise HTTPException(
                status_code=500,
                detail="Failed to sync holdings from any broker"
            )
        
        # Return first broker's info if specific broker requested
        broker_name = request.broker_id or synced_brokers[0]
        
        return {
            "status": "success",
            "broker": broker_name,
            "holdings": all_holdings,
            "last_synced": datetime.utcnow().isoformat(),
            "total_holdings": len(all_holdings)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sync portfolio failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to sync portfolio: {str(e)}")


@router.get("/status", response_model=BrokerStatusResponse)
async def get_broker_status(
    current_user: dict = Depends(get_current_user)
):
    """
    Get status of all connected brokers and total holdings
    """
    try:
        broker_connections = get_collection("broker_connections")
        holdings_collection = get_collection("holdings")
        
        if not broker_connections or not holdings_collection:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Get all connections
        connections = await broker_connections.find({
            "user_id": str(current_user["_id"])
        }).to_list(length=100)
        
        connected_brokers = []
        for conn in connections:
            connected_brokers.append({
                "broker": conn["broker"],
                "status": conn["status"],
                "connected_at": conn["connected_at"].isoformat(),
                "last_synced_at": conn.get("last_synced_at", conn["connected_at"]).isoformat()
            })
        
        # Get total holdings count
        total_holdings = await holdings_collection.count_documents({
            "user_id": str(current_user["_id"])
        })
        
        return {
            "connected_brokers": connected_brokers,
            "total_holdings": total_holdings
        }
        
    except Exception as e:
        logger.error(f"Get broker status failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get broker status: {str(e)}")


@router.delete("/disconnect")
async def disconnect_broker(
    broker_id: str = Query(..., description="Broker to disconnect"),
    current_user: dict = Depends(get_current_user)
):
    """
    Disconnect a broker and optionally remove holdings
    """
    try:
        broker_connections = get_collection("broker_connections")
        holdings_collection = get_collection("holdings")
        
        if not broker_connections or not holdings_collection:
            raise HTTPException(status_code=503, detail="Database not available")
        
        # Find connection
        connection = await broker_connections.find_one({
            "user_id": str(current_user["_id"]),
            "broker": broker_id
        })
        
        if not connection:
            raise HTTPException(
                status_code=404,
                detail=f"No connection found for {broker_id}"
            )
        
        # Delete connection
        await broker_connections.delete_one({"_id": connection["_id"]})
        
        # Delete holdings from this broker
        result = await holdings_collection.delete_many({
            "user_id": str(current_user["_id"]),
            "source": broker_id
        })
        
        return {
            "status": "success",
            "message": f"Disconnected from {broker_id}",
            "holdings_removed": result.deleted_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Disconnect broker failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to disconnect broker: {str(e)}")


# =============================================================================
# Helper Functions
# =============================================================================

async def _save_holdings(user_id: str, broker: str, holdings: List[Dict]):
    """Save holdings to database"""
    try:
        holdings_collection = get_collection("holdings")
        if not holdings_collection:
            logger.error("Holdings collection not available")
            return
        
        # Delete existing holdings from this broker
        await holdings_collection.delete_many({
            "user_id": user_id,
            "source": broker
        })
        
        # Insert new holdings
        if holdings:
            holdings_docs = []
            for holding in holdings:
                holdings_docs.append({
                    "user_id": user_id,
                    "source": broker,
                    "symbol": holding["symbol"],
                    "exchange": holding["exchange"],
                    "quantity": holding["quantity"],
                    "avg_price": holding["avg_price"],
                    "current_price": holding.get("current_price", 0),
                    "pnl": holding.get("pnl", 0),
                    "pnl_percentage": holding.get("pnl_percentage", 0),
                    "synced_at": datetime.utcnow()
                })
            
            await holdings_collection.insert_many(holdings_docs)
            logger.info(f"Saved {len(holdings_docs)} holdings for user {user_id} from {broker}")
    
    except Exception as e:
        logger.error(f"Failed to save holdings: {e}")
        raise
