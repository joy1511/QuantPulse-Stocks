"""
Authentication Router

Handles user registration, login, and authentication endpoints.
Uses MongoDB for user storage. NO DEMO MODE - Real authentication only.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address
from bson import ObjectId

from app.mongodb import get_collection
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserResponse,
    UserUpdate,
    PasswordChange,
    Token,
    MessageResponse
)
from app.services.auth_service import (
    get_password_hash,
    verify_password,
    authenticate_user,
    create_access_token,
    get_current_user,
    get_current_active_user
)

# Rate limiter for security against brute force attacks
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# =============================================================================
# User Registration
# =============================================================================

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserRegister):
    """
    Register a new user account.
    
    - **email**: Valid email address
    - **password**: Minimum 8 characters
    - **full_name**: Optional full name
    
    Returns user object with JWT token.
    """
    users_collection = get_collection("users")
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Check if user already exists
    existing_user = await users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user document
    user_doc = {
        "email": user_data.email,
        "hashed_password": get_password_hash(user_data.password),
        "full_name": user_data.full_name or "",
        "is_active": True,
        "is_verified": False,
        "is_admin": False,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    # Insert into MongoDB
    result = await users_collection.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    # Return user response (exclude password)
    return {
        "id": str(result.inserted_id),
        "email": user_doc["email"],
        "full_name": user_doc["full_name"],
        "is_active": user_doc["is_active"],
        "is_verified": user_doc["is_verified"],
        "created_at": user_doc["created_at"],
        "last_login": user_doc["last_login"]
    }

# =============================================================================
# User Login (Rate Limited to Prevent Brute Force Attacks)
# =============================================================================

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login with email and password.
    
    - **username**: User email
    - **password**: User password
    
    Returns JWT access token.
    """
    users_collection = get_collection("users")
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Authenticate user
    user = await authenticate_user(form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": str(user["_id"])}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "is_active": user.get("is_active", True),
            "is_verified": user.get("is_verified", False),
            "created_at": user.get("created_at"),
            "last_login": datetime.utcnow()
        }
    }

@router.post("/login/json", response_model=Token)
@limiter.limit("5/minute")  # Max 5 login attempts per minute
async def login_json(
    request: Request,
    user_data: UserLogin
):
    """
    Login with JSON payload.
    
    - **email**: User email
    - **password**: User password
    
    Returns JWT access token.
    """
    users_collection = get_collection("users")
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Authenticate user
    user = await authenticate_user(user_data.email, user_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await users_collection.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user["email"], "user_id": str(user["_id"])}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user["_id"]),
            "email": user["email"],
            "full_name": user.get("full_name", ""),
            "is_active": user.get("is_active", True),
            "is_verified": user.get("is_verified", False),
            "created_at": user.get("created_at"),
            "last_login": datetime.utcnow()
        }
    }

# =============================================================================
# Get Current User
# =============================================================================

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """
    Get current authenticated user information.
    
    Requires valid JWT token in Authorization header.
    """
    return {
        "id": str(current_user["_id"]),
        "email": current_user["email"],
        "full_name": current_user.get("full_name", ""),
        "is_active": current_user.get("is_active", True),
        "is_verified": current_user.get("is_verified", False),
        "created_at": current_user.get("created_at"),
        "last_login": current_user.get("last_login")
    }

# =============================================================================
# Update User Profile
# =============================================================================

@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    user_update: UserUpdate,
    current_user: dict = Depends(get_current_user)
):
    """
    Update current user's profile information.
    
    - **email**: New email (optional)
    - **full_name**: New full name (optional)
    """
    users_collection = get_collection("users")
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    update_data = {}
    
    if user_update.email:
        # Check if new email is already taken
        existing = await users_collection.find_one({"email": user_update.email})
        if existing and str(existing["_id"]) != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        update_data["email"] = user_update.email
    
    if user_update.full_name:
        update_data["full_name"] = user_update.full_name
    
    if update_data:
        await users_collection.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_data}
        )
    
    # Get updated user
    updated_user = await users_collection.find_one({"_id": current_user["_id"]})
    
    return {
        "id": str(updated_user["_id"]),
        "email": updated_user["email"],
        "full_name": updated_user.get("full_name", ""),
        "is_active": updated_user.get("is_active", True),
        "is_verified": updated_user.get("is_verified", False),
        "created_at": updated_user.get("created_at"),
        "last_login": updated_user.get("last_login")
    }

# =============================================================================
# Change Password
# =============================================================================

@router.post("/change-password", response_model=MessageResponse)
async def change_password(
    password_data: PasswordChange,
    current_user: dict = Depends(get_current_user)
):
    """
    Change current user's password.
    
    - **old_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    """
    users_collection = get_collection("users")
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Verify old password
    if not verify_password(password_data.old_password, current_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect current password"
        )
    
    # Update password
    new_hashed_password = get_password_hash(password_data.new_password)
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"hashed_password": new_hashed_password}}
    )
    
    return {
        "message": "Password changed successfully",
        "detail": "Please login again with your new password"
    }

# =============================================================================
# Delete Account
# =============================================================================

@router.delete("/me", response_model=MessageResponse)
async def delete_account(current_user: dict = Depends(get_current_user)):
    """
    Deactivate current user's account.
    
    Sets is_active to False instead of deleting the account.
    """
    users_collection = get_collection("users")
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    # Deactivate account
    await users_collection.update_one(
        {"_id": current_user["_id"]},
        {"$set": {"is_active": False}}
    )
    
    return {
        "message": "Account deactivated successfully",
        "detail": "Your account has been deactivated. Contact support to reactivate."
    }

# =============================================================================
# Google OAuth Login
# =============================================================================

from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from fastapi.responses import RedirectResponse
import os

# OAuth configuration
config = Config(environ=os.environ)
oauth = OAuth(config)

oauth.register(
    name='google',
    client_id=os.getenv('GOOGLE_CLIENT_ID'),
    client_secret=os.getenv('GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

@router.get("/google/login")
async def google_login(request: Request):
    """
    Initiate Google OAuth login flow.
    
    Redirects user to Google's login page.
    """
    redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8000/api/auth/google/callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request):
    """
    Handle Google OAuth callback.
    
    Creates or logs in user with Google account.
    Returns JWT token for authentication.
    """
    users_collection = get_collection("users")
    if users_collection is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection not available"
        )
    
    try:
        # Get access token from Google
        token = await oauth.google.authorize_access_token(request)
        
        # Get user info from Google
        user_info = token.get('userinfo')
        if not user_info:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get user info from Google"
            )
        
        email = user_info.get('email')
        full_name = user_info.get('name')
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Check if user exists
        user = await users_collection.find_one({"email": email})
        
        if not user:
            # Create new user
            user_doc = {
                "email": email,
                "hashed_password": get_password_hash(os.urandom(32).hex()),  # Random password for OAuth users
                "full_name": full_name or "",
                "is_active": True,
                "is_verified": True,  # Google users are pre-verified
                "is_admin": False,
                "created_at": datetime.utcnow(),
                "last_login": datetime.utcnow()
            }
            result = await users_collection.insert_one(user_doc)
            user_id = str(result.inserted_id)
        else:
            # Update last login
            await users_collection.update_one(
                {"_id": user["_id"]},
                {"$set": {"last_login": datetime.utcnow()}}
            )
            user_id = str(user["_id"])
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": email, "user_id": user_id}
        )
        
        # Redirect to frontend with token
        frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
        return RedirectResponse(
            url=f"{frontend_url}/auth/callback?token={access_token}"
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Google authentication failed: {str(e)}"
        )
