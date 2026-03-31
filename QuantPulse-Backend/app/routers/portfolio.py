"""
Portfolio Router

Handles user portfolio/holdings management with MongoDB storage.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field

from app.mongodb import get_collection
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api/portfolio", tags=["Portfolio"])

# =============================================================================
# Schemas
# =============================================================================

class HoldingCreate(BaseModel):
    """Schema for creating a new holding"""
    symbol: str = Field(..., min_length=1, max_length=20)
    buy_price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    buy_date: str  # ISO date string (YYYY-MM-DD)
    notes: Optional[str] = Field(None, max_length=500)

class HoldingUpdate(BaseModel):
    """Schema for updating a holding"""
    symbol: Optional[str] = Field(None, min_length=1, max_length=20)
    buy_price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, gt=0)
    buy_date: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=500)

class HoldingResponse(BaseModel):
    """Schema for holding response"""
    id: str
    symbol: str
    buy_price: float
    quantity: int
    buy_date: str
    notes: str
    created_at: str
    user_id: str

# =============================================================================
# Get All Holdings
# =============================================================================

@router.get("/holdings", response_model=List[HoldingResponse])
async def get_holdings(current_user: dict = Depends(get_current_user)):
    """
    Get all holdings for the current user.
    
    Returns list of holdings sorted by creation date (newest first).
    """
    holdings_collection = get_collection("holdings")
    if holdings_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Find all holdings for this user
    cursor = holdings_collection.find({"user_id": str(current_user["_id"])})
    holdings = await cursor.to_list(length=None)
    
    # Convert to response format
    result = []
    for holding in holdings:
        result.append({
            "id": str(holding["_id"]),
            "symbol": holding["symbol"],
            "buy_price": holding["buy_price"],
            "quantity": holding["quantity"],
            "buy_date": holding["buy_date"],
            "notes": holding.get("notes", ""),
            "created_at": holding["created_at"].isoformat() if isinstance(holding["created_at"], datetime) else holding["created_at"],
            "user_id": holding["user_id"]
        })
    
    # Sort by created_at descending
    result.sort(key=lambda x: x["created_at"], reverse=True)
    
    return result

# =============================================================================
# Add Holding
# =============================================================================

@router.post("/holdings", response_model=HoldingResponse, status_code=status.HTTP_201_CREATED)
async def add_holding(
    holding_data: HoldingCreate,
    current_user: dict = Depends(get_current_user)
):
    """
    Add a new holding to the user's portfolio.
    
    - **symbol**: Stock symbol (e.g., RELIANCE, TCS)
    - **buy_price**: Purchase price per share
    - **quantity**: Number of shares
    - **buy_date**: Purchase date (YYYY-MM-DD)
    - **notes**: Optional notes
    """
    holdings_collection = get_collection("holdings")
    if holdings_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Clean symbol (remove .NS or .BO suffix)
    clean_symbol = holding_data.symbol.upper().replace(".NS", "").replace(".BO", "")
    
    # Create holding document
    holding_doc = {
        "user_id": str(current_user["_id"]),
        "symbol": clean_symbol,
        "buy_price": holding_data.buy_price,
        "quantity": holding_data.quantity,
        "buy_date": holding_data.buy_date,
        "notes": holding_data.notes or "",
        "created_at": datetime.utcnow()
    }
    
    # Insert into MongoDB
    result = await holdings_collection.insert_one(holding_doc)
    
    return {
        "id": str(result.inserted_id),
        "symbol": clean_symbol,
        "buy_price": holding_data.buy_price,
        "quantity": holding_data.quantity,
        "buy_date": holding_data.buy_date,
        "notes": holding_data.notes or "",
        "created_at": holding_doc["created_at"].isoformat(),
        "user_id": str(current_user["_id"])
    }

# =============================================================================
# Update Holding
# =============================================================================

@router.put("/holdings/{holding_id}", response_model=HoldingResponse)
async def update_holding(
    holding_id: str,
    holding_data: HoldingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update an existing holding.
    
    Only the holding owner can update it.
    """
    holdings_collection = get_collection("holdings")
    if holdings_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Validate ObjectId
    try:
        obj_id = ObjectId(holding_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid holding ID"
        )
    
    # Find holding
    holding = await holdings_collection.find_one({
        "_id": obj_id,
        "user_id": str(current_user["_id"])
    })
    
    if not holding:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holding not found"
        )
    
    # Build update data
    update_data = {}
    if holding_data.symbol is not None:
        update_data["symbol"] = holding_data.symbol.upper().replace(".NS", "").replace(".BO", "")
    if holding_data.buy_price is not None:
        update_data["buy_price"] = holding_data.buy_price
    if holding_data.quantity is not None:
        update_data["quantity"] = holding_data.quantity
    if holding_data.buy_date is not None:
        update_data["buy_date"] = holding_data.buy_date
    if holding_data.notes is not None:
        update_data["notes"] = holding_data.notes
    
    if update_data:
        await holdings_collection.update_one(
            {"_id": obj_id},
            {"$set": update_data}
        )
    
    # Get updated holding
    updated_holding = await holdings_collection.find_one({"_id": obj_id})
    
    return {
        "id": str(updated_holding["_id"]),
        "symbol": updated_holding["symbol"],
        "buy_price": updated_holding["buy_price"],
        "quantity": updated_holding["quantity"],
        "buy_date": updated_holding["buy_date"],
        "notes": updated_holding.get("notes", ""),
        "created_at": updated_holding["created_at"].isoformat() if isinstance(updated_holding["created_at"], datetime) else updated_holding["created_at"],
        "user_id": updated_holding["user_id"]
    }

# =============================================================================
# Delete Holding
# =============================================================================

@router.delete("/holdings/{holding_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_holding(
    holding_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a holding from the portfolio.
    
    Only the holding owner can delete it.
    """
    holdings_collection = get_collection("holdings")
    if holdings_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Validate ObjectId
    try:
        obj_id = ObjectId(holding_id)
    except:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid holding ID"
        )
    
    # Delete holding (only if owned by current user)
    result = await holdings_collection.delete_one({
        "_id": obj_id,
        "user_id": str(current_user["_id"])
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Holding not found"
        )
    
    return None
