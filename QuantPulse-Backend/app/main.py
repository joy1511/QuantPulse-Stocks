"""
QuantPulse India Backend - Production-Grade Market Data Engine

This is the main FastAPI application file that:
1. Creates and configures the FastAPI app instance
2. Sets up CORS middleware for frontend communication
3. Registers all API routers
4. Initializes logging and configuration
5. Sets up the production-grade stock data system
6. Implements security protections against attacks

Architecture:
- Multi-provider stock data with automatic fallback
- Production-grade caching with request coalescing
- Stale-while-revalidate pattern for optimal performance
- Automatic demo mode when providers fail
- Clean separation of concerns with service layers
- Security middleware for attack prevention

To run this application:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    
Or simply:
    python run.py
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.middleware.sessions import SessionMiddleware
import logging
import time
import os

# Import configuration and setup
from app.config import (
    APP_NAME,
    APP_VERSION,
    APP_DESCRIPTION,
    ALLOWED_ORIGINS,
    DEMO_MODE,
    IS_RAILWAY,
    setup_logging,
    validate_and_log_configuration
)

# Import routers
from app.routers import health
from app.routers import stocks
from app.routers import news
from app.routers import predictions
from app.routers import ensemble
from app.routers import v2_analysis
from app.routers import auth

# Setup logging first
setup_logging()
logger = logging.getLogger(__name__)

# =============================================================================
# Security: Rate Limiting Setup
# =============================================================================

limiter = Limiter(key_func=get_remote_address)

# =============================================================================
# Create FastAPI Application
# =============================================================================

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url="/docs",       # Swagger UI available at /docs
    redoc_url="/redoc",     # ReDoc available at /redoc
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# =============================================================================
# Security Middleware
# =============================================================================

# 1. Session Middleware (Required for OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv('SECRET_KEY', 'your-secret-key-here')
)

# 2. Trusted Host Middleware - Prevents Host Header attacks
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"]  # In production: ["yourdomain.com", "*.yourdomain.com"]
)

# 2. Security Headers Middleware
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    
    # Prevent clickjacking attacks
    response.headers["X-Frame-Options"] = "DENY"
    
    # Prevent MIME type sniffing
    response.headers["X-Content-Type-Options"] = "nosniff"
    
    # Enable XSS protection
    response.headers["X-XSS-Protection"] = "1; mode=block"
    
    # Strict Transport Security (HTTPS only)
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    # Content Security Policy
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    
    # Referrer Policy
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    
    # Permissions Policy
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    
    return response

# 3. Request Logging and Monitoring
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests for security monitoring"""
    start_time = time.time()
    
    # Log request details
    logger.info(f"Request: {request.method} {request.url.path} from {request.client.host}")
    
    response = await call_next(request)
    
    # Log response time
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    logger.info(f"Response: {response.status_code} in {process_time:.3f}s")
    
    return response

# =============================================================================
# CORS Middleware Configuration
# =============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# GZip Compression Middleware (High Performance)
# =============================================================================

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000  # Only compress responses larger than 1KB
)

# =============================================================================
# Register Routers
# =============================================================================

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(stocks.router)
app.include_router(news.router)
app.include_router(predictions.router)
app.include_router(ensemble.router)
app.include_router(v2_analysis.router)

# =============================================================================
# Application Startup
# =============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    
    # Initialize database
    from app.database import init_db
    init_db()
    
    # Validate configuration and log startup information
    config_status = validate_and_log_configuration()
    
    # Initialize services (they will self-configure based on available keys)
    from app.services.stock_service import stock_service
    service_status = stock_service.get_service_status()
    
    logger.info("🏗️ Production-grade market data engine initializing...")
    logger.info(f"📊 Stock service status: {service_status['status']}")
    logger.info(f"🔧 Provider mode: {service_status['provider_status']['mode']}")
    
    if service_status['provider_status']['primary_available']:
        logger.info("✅ Primary provider (TwelveData) available")
    
    if service_status['provider_status']['fallback_available']:
        logger.info("✅ Fallback provider (Finnhub) available")
    
    if DEMO_MODE:
        logger.warning("🔄 Running in DEMO MODE - serving simulated data")
        if IS_RAILWAY:
            logger.warning("🔄 Configure API keys in Railway dashboard for live data")
        else:
            logger.warning("🔄 To enable live data, configure TWELVEDATA_API_KEY or FINNHUB_API_KEY")
    else:
        logger.info("📊 Running in LIVE MODE - serving real market data")
    
    # Pre-load TensorFlow at startup (when memory is available)
    logger.info("🧠 Pre-loading TensorFlow to avoid OOM during requests...")
    try:
        import os
        os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
        import tensorflow as tf
        tf.get_logger().setLevel("ERROR")
        logger.info("✅ TensorFlow pre-loaded successfully")
    except Exception as e:
        logger.warning(f"⚠️ TensorFlow pre-load failed: {e}")
        logger.warning("⚠️ LSTM predictions will be unavailable")
    
    logger.info("🎯 Application startup complete - ready to serve requests")
    logger.info("ℹ️ LSTM model will load on first prediction request")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("🛑 Application shutting down...")
    
    # Clear cache and cleanup background tasks
    from app.services.cache_service import cache_service
    cache_service.clear_all()
    
    logger.info("✅ Shutdown complete")

# =============================================================================
# Root Endpoint
# =============================================================================

@app.get("/", tags=["Root"])
async def root():
    """
    Root Endpoint
    
    Provides a welcome message and basic API information.
    This is the first endpoint users will see when accessing the API directly.
    
    Returns:
        dict: Welcome message with API information
    """
    from app.services.stock_service import stock_service
    service_status = stock_service.get_service_status()
    
    return {
        "message": "Welcome to QuantPulse India API",
        "description": "Production-grade AI-powered stock market analytics for NSE",
        "version": APP_VERSION,
        "architecture": "Multi-provider with intelligent fallback",
        "features": [
            "Real-time stock quotes",
            "Historical data analysis", 
            "Company profiles",
            "Production-grade caching",
            "Automatic provider fallback",
            "Demo mode support"
        ],
        "docs": "/docs",
        "health": "/health",
        "service_status": {
            "stock_service": service_status["status"],
            "provider_mode": service_status["provider_status"]["mode"],
            "demo_mode": DEMO_MODE,
            "live_providers_available": service_status["provider_status"]["primary_available"] or service_status["provider_status"]["fallback_available"]
        }
    }
