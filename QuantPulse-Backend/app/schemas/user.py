"""
User Pydantic Schemas

Defines request/response schemas for user-related API endpoints.
Provides data validation and serialization.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime

# =============================================================================
# User Registration & Authentication Schemas
# =============================================================================

class UserRegister(BaseModel):
    """Schema for user registration (DUMMY MODE - no validation)"""
    email: str  # Changed from EmailStr to accept any string
    password: str  # Removed min_length validation
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    """Schema for user login (DUMMY MODE - no validation)"""
    email: str  # Changed from EmailStr to accept any string
    password: str

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class TokenData(BaseModel):
    """Schema for token payload data"""
    email: Optional[str] = None
    user_id: Optional[int] = None

# =============================================================================
# User Response Schemas
# =============================================================================

class UserResponse(BaseModel):
    """Schema for user data in responses (excludes sensitive info)"""
    id: int
    email: str
    full_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: Optional[datetime]
    last_login: Optional[datetime]
    
    class Config:
        from_attributes = True  # Pydantic v2 (was orm_mode in v1)

class UserUpdate(BaseModel):
    """Schema for updating user profile (DUMMY MODE - no validation)"""
    full_name: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = None  # Changed from EmailStr to accept any string

class PasswordChange(BaseModel):
    """Schema for changing password"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)
    
    @validator('new_password')
    def password_strength(cls, v):
        """Validate password strength"""
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v

# =============================================================================
# Response Messages
# =============================================================================

class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    detail: Optional[str] = None
