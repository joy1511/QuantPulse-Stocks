"""
Authentication Router

Handles user registration, login, and authentication endpoints.
Includes rate limiting to prevent brute force attacks.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.database import get_db
from app.models.user import User
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
def register_user(user_data: UserRegister):
    """
    Register a new user account (DUMMY MODE - accepts any credentials).
    
    - **email**: Any email format
    - **password**: Any password
    - **full_name**: Optional full name
    
    Returns a dummy user object.
    """
    # DUMMY MODE: Skip database, return fake user
    from datetime import datetime
    
    # Create a dummy user response without database
    dummy_user = {
        "id": 1,
        "email": user_data.email,
        "full_name": user_data.full_name or "Demo User",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "last_login": None
    }
    
    return dummy_user

# =============================================================================
# User Login (Rate Limited to Prevent Brute Force Attacks)
# =============================================================================

@router.post("/login", response_model=Token)
@limiter.limit("5/minute")  # Max 5 login attempts per minute
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Login with email and password (DUMMY MODE - accepts any credentials).
    
    - **username**: Any email
    - **password**: Any password
    
    Returns JWT access token.
    """
    from datetime import datetime
    
    # DUMMY MODE: Accept any credentials
    dummy_user = {
        "id": 1,
        "email": form_data.username,
        "full_name": "Demo User",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow()
    }
    
    # Create access token
    access_token = create_access_token(
        data={"sub": form_data.username, "user_id": 1}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": dummy_user
    }

@router.post("/login/json", response_model=Token)
@limiter.limit("5/minute")  # Max 5 login attempts per minute
def login_json(
    request: Request,
    user_data: UserLogin
):
    """
    Login with JSON payload (DUMMY MODE - accepts any credentials).
    
    - **email**: Any email
    - **password**: Any password
    
    Returns JWT access token.
    """
    from datetime import datetime
    
    # DUMMY MODE: Accept any credentials
    dummy_user = {
        "id": 1,
        "email": user_data.email,
        "full_name": "Demo User",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow()
    }
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user_data.email, "user_id": 1}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": dummy_user
    }

# =============================================================================
# Get Current User
# =============================================================================

@router.get("/me", response_model=UserResponse)
def get_current_user_info():
    """
    Get current authenticated user information (DUMMY MODE).
    
    Returns dummy user data without token validation.
    """
    from datetime import datetime
    
    # DUMMY MODE: Return fake user data
    dummy_user = {
        "id": 1,
        "email": "demo@user.com",
        "full_name": "Demo User",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow()
    }
    
    return dummy_user

# =============================================================================
# Update User Profile
# =============================================================================

@router.put("/me", response_model=UserResponse)
def update_user_profile(user_update: UserUpdate):
    """
    Update current user's profile information (DUMMY MODE).
    
    Returns dummy user data.
    """
    from datetime import datetime
    
    # DUMMY MODE: Return fake updated user
    dummy_user = {
        "id": 1,
        "email": user_update.email or "demo@user.com",
        "full_name": user_update.full_name or "Demo User",
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "last_login": datetime.utcnow()
    }
    
    return dummy_user

# =============================================================================
# Change Password
# =============================================================================

@router.post("/change-password", response_model=MessageResponse)
def change_password(password_data: PasswordChange):
    """
    Change current user's password (DUMMY MODE).
    
    Always succeeds.
    """
    return {
        "message": "Password changed successfully",
        "detail": "Please login again with your new password"
    }

# =============================================================================
# Delete Account
# =============================================================================

@router.delete("/me", response_model=MessageResponse)
def delete_account():
    """
    Delete current user's account (DUMMY MODE).
    
    Always succeeds.
    """
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
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback.
    
    Creates or logs in user with Google account.
    Returns JWT token for authentication.
    """
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
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            # Create new user with Google account
            user = User(
                email=email,
                full_name=full_name,
                hashed_password="",  # No password for OAuth users
                is_active=True,
                is_verified=True,  # Google accounts are pre-verified
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        # Create JWT token
        access_token = create_access_token(
            data={"sub": user.email, "user_id": user.id}
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
