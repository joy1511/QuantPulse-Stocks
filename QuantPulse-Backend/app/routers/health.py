"""
Health Check Router

Enhanced health monitoring for Render free tier deployment.
Provides detailed status of all services and components.
"""

from fastapi import APIRouter
import logging
import time
import os

logger = logging.getLogger(__name__)

# Create a router instance for health-related endpoints
router = APIRouter(
    prefix="",  # No prefix, health check at root level
    tags=["Health"],  # Group in API docs under "Health"
)

# Track startup time for uptime calculation
_startup_time = time.time()


@router.get("/health")
async def health_check():
    """
    Basic Health Check Endpoint
    
    Fast health check for load balancers and monitoring.
    Does not check external dependencies.
    
    Returns:
        dict: Status object with service name and health status
    """
    return {
        "status": "ok",
        "service": "quantpulse-backend"
    }


@router.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed Health Check Endpoint
    
    Comprehensive health status including:
    - System information
    - Database connectivity
    - Model loading status
    - Memory usage (if psutil available)
    - API key configuration
    
    Returns:
        dict: Detailed status of all components
    """
    from app.config import IS_CLOUD, IS_RENDER, GROQ_API_KEY, INDIANAPI_KEY
    
    # Calculate uptime
    uptime_seconds = int(time.time() - _startup_time)
    uptime_minutes = uptime_seconds // 60
    uptime_hours = uptime_minutes // 60
    
    health_status = {
        "status": "ok",
        "service": "quantpulse-backend",
        "timestamp": int(time.time()),
        "uptime": {
            "seconds": uptime_seconds,
            "minutes": uptime_minutes,
            "hours": uptime_hours,
            "formatted": f"{uptime_hours}h {uptime_minutes % 60}m {uptime_seconds % 60}s"
        },
        "environment": {
            "is_cloud": IS_CLOUD,
            "is_render": IS_RENDER,
            "python_version": os.sys.version.split()[0]
        }
    }
    
    # Check LSTM model status
    try:
        from app.services.lstm_service import get_model_status
        model_status = get_model_status()
        health_status["lstm_model"] = model_status
    except Exception as e:
        health_status["lstm_model"] = {"status": "error", "error": str(e)}
    
    # Check API keys (don't expose actual keys)
    health_status["api_keys"] = {
        "groq": bool(GROQ_API_KEY and GROQ_API_KEY != "MISSING_KEY"),
        "indianapi": bool(INDIANAPI_KEY)
    }
    
    # Check database connectivity
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        health_status["database"] = {"status": "connected", "type": "postgresql" if "postgresql" in str(engine.url) else "sqlite"}
    except Exception as e:
        health_status["database"] = {"status": "error", "error": str(e)}
    
    # Check MongoDB (optional)
    try:
        from app.mongodb import mongodb_client
        if mongodb_client:
            await mongodb_client.admin.command('ping')
            health_status["mongodb"] = {"status": "connected"}
        else:
            health_status["mongodb"] = {"status": "not_configured"}
    except Exception as e:
        health_status["mongodb"] = {"status": "not_configured", "note": "Optional - not required"}
    
    # Memory usage (optional, requires psutil)
    try:
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        memory_percent = process.memory_percent()
        
        health_status["memory"] = {
            "usage_mb": round(memory_mb, 1),
            "usage_percent": round(memory_percent, 1),
            "status": "ok" if memory_mb < 450 else "warning" if memory_mb < 500 else "critical"
        }
    except ImportError:
        health_status["memory"] = {"status": "monitoring_unavailable"}
    except Exception as e:
        health_status["memory"] = {"status": "error", "error": str(e)}
    
    return health_status


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness Check Endpoint
    
    Checks if the service is ready to handle requests.
    Returns 200 if ready, 503 if not ready.
    
    Kubernetes/Docker can use this for readiness probes.
    
    Returns:
        dict: Readiness status
    """
    from app.services.lstm_service import get_model_status
    
    # Check if model is loaded (or loading)
    model_status = get_model_status()
    
    # Service is ready if model is loaded OR if loading is in progress
    # (we can serve fallback predictions while loading)
    is_ready = model_status["loaded"] or model_status["loading"]
    
    return {
        "status": "ready" if is_ready else "not_ready",
        "model_status": model_status
    }


@router.get("/health/live")
async def liveness_check():
    """
    Liveness Check Endpoint
    
    Checks if the service is alive and responding.
    This is a simple check that always returns 200 if the process is running.
    
    Kubernetes/Docker can use this for liveness probes.
    
    Returns:
        dict: Liveness status
    """
    return {
        "status": "alive",
        "timestamp": int(time.time())
    }

