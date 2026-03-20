"""
QuantPulse Backend Configuration

Production-grade configuration with multi-provider stock data support.
Safely handles local development, Railway, and Render cloud deployment.
"""

import os
import logging

# =============================================================================
# Environment Detection and Configuration Loading
# =============================================================================

# Detect environment (Railway sets RAILWAY_ENVIRONMENT, Render sets RENDER)
ENV = os.getenv("ENV", "development")
IS_RAILWAY = os.getenv("RAILWAY_ENVIRONMENT") is not None
IS_RENDER = os.getenv("RENDER") is not None
IS_CLOUD = IS_RAILWAY or IS_RENDER

# Load .env ONLY for local development (not on cloud)
if not IS_CLOUD:
    try:
        from dotenv import load_dotenv
        load_dotenv()
        print(f"🔧 Running in {ENV} mode - loaded .env file")
    except ImportError:
        print(f"🔧 Running in {ENV} mode - python-dotenv not installed")
    except Exception as e:
        print(f"🔧 Running in {ENV} mode - .env loading failed: {e}")
else:
    platform = "Render" if IS_RENDER else "Railway"
    print(f"🚀 Running on {platform} - using environment variables")

# =============================================================================
# Application Metadata
# =============================================================================

APP_NAME = "QuantPulse India Backend"
APP_VERSION = "2.0.0"
APP_DESCRIPTION = "Production-grade backend API with multi-provider stock data engine"

# =============================================================================
# API Keys Configuration
# =============================================================================

# Stock Data Provider API Keys
INDIANAPI_KEY = os.getenv("INDIANAPI_KEY")  # FREE tier works without key
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
STOCK_PROVIDER = os.getenv("STOCK_PROVIDER", "auto")  # auto, indianapi, twelvedata, finnhub, demo

# News API Configuration
NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")

# AI / LLM API Keys (for War Room agents)
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "MISSING_KEY")
SERPER_API_KEY = os.getenv("SERPER_API_KEY", "MISSING_KEY")

# Security Keys
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production-please-use-strong-key")

# Hugging Face Token (for downloading LSTM model)
HF_TOKEN = os.getenv("HF_TOKEN", None)  # None = public repo, no token needed

# =============================================================================
# Demo Mode Detection
# =============================================================================

# V2 pipeline uses yfinance exclusively — demo mode is no longer relevant
# Force False so legacy V1 startup logs don't print scary warnings
DEMO_MODE = False

# =============================================================================
# Server Configuration
# =============================================================================

HOST = "0.0.0.0"
PORT = int(os.getenv("PORT", 8000))  # Railway injects PORT dynamically

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://localhost:8080",
    # Render deployments
    "https://quantpulse.onrender.com",
    "https://quantpulse-frontend.onrender.com",
    # Vercel / Netlify (if deployed there)
    "https://quantpulse.vercel.app",
    "https://quantpulse.netlify.app",
]

# Also allow any subdomain on onrender.com via env var override
_extra_origins = os.getenv("ALLOWED_ORIGINS", "")
if _extra_origins:
    ALLOWED_ORIGINS.extend([o.strip() for o in _extra_origins.split(",") if o.strip()])

# =============================================================================
# Cache Configuration
# =============================================================================

CACHE_MAX_SIZE = int(os.getenv("CACHE_MAX_SIZE", 10000))
CACHE_DEFAULT_TTL = int(os.getenv("CACHE_DEFAULT_TTL", 3600))

# =============================================================================
# Logging Configuration
# =============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")

def setup_logging():
    """Setup application logging with environment-appropriate configuration"""
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    logging.basicConfig(
        level=getattr(logging, LOG_LEVEL.upper()),
        format=log_format,
        datefmt=date_format
    )
    
    # Log environment info
    logger = logging.getLogger(__name__)
    logger.info(f"🔧 Environment: {ENV}")
    logger.info(f"📊 Log Level: {LOG_LEVEL}")
    logger.info(f"🚀 Railway Deployment: {IS_RAILWAY}")

# =============================================================================
# Startup Validation and Logging
# =============================================================================

def validate_and_log_configuration():
    """
    Validate configuration and log startup information.
    This function is called during application startup.
    """
    logger = logging.getLogger(__name__)
    
    # Log environment and basic info
    logger.info("=" * 60)
    logger.info(f"🚀 {APP_NAME} v{APP_VERSION}")
    logger.info(f"🔧 Environment: {ENV}")
    logger.info(f"🌐 Server: http://{HOST}:{PORT}")
    logger.info(f"☁️ Railway: {IS_RAILWAY}")
    logger.info("=" * 60)
    
    # STEP 6 — Add Startup Logging (API key availability without printing keys)
    print("=" * 50)
    print("API KEY STATUS:")
    print(f"INDIANAPI_KEY loaded: {bool(INDIANAPI_KEY)} (FREE tier works without key)")
    print(f"NEWSAPI_KEY loaded: {bool(NEWSAPI_KEY)}")
    print(f"FINNHUB_API_KEY loaded: {bool(FINNHUB_API_KEY)}")
    print(f"TWELVEDATA_API_KEY loaded: {bool(TWELVEDATA_API_KEY)}")
    print(f"GROQ_API_KEY loaded: {GROQ_API_KEY != 'MISSING_KEY'}")
    print(f"SERPER_API_KEY loaded: {SERPER_API_KEY != 'MISSING_KEY'}")
    print(f"HF_TOKEN loaded: {bool(HF_TOKEN)}")
    print(f"DEMO_MODE: {DEMO_MODE}")
    print("=" * 50)
    
    # Validate and log API key status
    api_keys_available = []
    api_keys_missing = []
    
    # Stock API Keys
    if INDIANAPI_KEY:
        logger.info("✅ INDIANAPI_KEY loaded - IndianAPI premium features available (PRIMARY)")
        api_keys_available.append("IndianAPI (Premium - Primary)")
    else:
        logger.info("ℹ️ INDIANAPI_KEY not set - using FREE tier (works without key)")
        api_keys_available.append("IndianAPI (FREE - Primary)")
    
    if TWELVEDATA_API_KEY:
        logger.info("ℹ️ TWELVEDATA_API_KEY loaded - disabled in AUTO mode (Indian stocks not supported)")
    
    if FINNHUB_API_KEY:
        logger.info("ℹ️ FINNHUB_API_KEY loaded - disabled in AUTO mode (Indian stocks not supported)")
    
    # News API Key
    if NEWSAPI_KEY:
        logger.info("✅ NEWSAPI_KEY loaded - news service available")
        api_keys_available.append("NewsAPI")
    else:
        logger.warning("⚠️ NEWSAPI_KEY missing - news service may be limited")
        api_keys_missing.append("NewsAPI")
    
    # Demo Mode Detection
    if DEMO_MODE:
        logger.warning("🔄 No stock API keys detected - running in DEMO MODE")
        logger.warning("🔄 All stock data will be simulated for demonstration")
        if IS_RAILWAY:
            logger.error("❌ RAILWAY deployment without API keys - configure them in Railway dashboard!")
    else:
        logger.info("📊 API keys detected - running in LIVE MODE")
        logger.info(f"📊 Available providers: {', '.join(api_keys_available)}")
    
    # Stock Provider Mode
    logger.info(f"📊 Stock provider mode: {STOCK_PROVIDER}")
    
    # Cache Configuration
    logger.info(f"💾 Cache configuration: max_size={CACHE_MAX_SIZE}, default_ttl={CACHE_DEFAULT_TTL}s")
    
    # Security reminder for production
    if IS_RAILWAY and api_keys_missing:
        logger.warning("🔐 Security reminder: Set API keys in Railway dashboard for production")
    
    logger.info("=" * 60)
    
    return {
        "environment": ENV,
        "is_railway": IS_RAILWAY,
        "demo_mode": DEMO_MODE,
        "api_keys_available": api_keys_available,
        "api_keys_missing": api_keys_missing,
        "stock_provider_mode": STOCK_PROVIDER
    }

# =============================================================================
# Configuration Export
# =============================================================================

# Export all configuration for easy importing
__all__ = [
    # Environment
    "ENV",
    "IS_RAILWAY",
    "IS_RENDER",
    "IS_CLOUD",
    "DEMO_MODE",
    
    # Application
    "APP_NAME",
    "APP_VERSION", 
    "APP_DESCRIPTION",
    
    # API Keys
    "INDIANAPI_KEY",
    "TWELVEDATA_API_KEY",
    "FINNHUB_API_KEY",
    "NEWSAPI_KEY",
    "GROQ_API_KEY",
    "SERPER_API_KEY",
    "HF_TOKEN",
    "STOCK_PROVIDER",
    
    # Server
    "HOST",
    "PORT",
    "ALLOWED_ORIGINS",
    
    # Cache
    "CACHE_MAX_SIZE",
    "CACHE_DEFAULT_TTL",
    
    # Logging
    "LOG_LEVEL",
    
    # Functions
    "setup_logging",
    "validate_and_log_configuration"
]
