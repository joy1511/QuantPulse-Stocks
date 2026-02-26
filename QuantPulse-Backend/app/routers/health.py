"""
Health Check Router

This module provides health check endpoints for monitoring the API status.
These endpoints are useful for:
- Load balancers to verify the service is running
- Kubernetes/Docker health probes
- Monitoring dashboards
"""

from fastapi import APIRouter

# Create a router instance for health-related endpoints
router = APIRouter(
    prefix="",  # No prefix, health check at root level
    tags=["Health"],  # Group in API docs under "Health"
)


@router.get("/health")
async def health_check():
    """
    Health Check Endpoint
    
    Returns the current status of the backend service.
    This endpoint should always return quickly and not depend on external services.
    
    Returns:
        dict: Status object with service name and health status
    """
    return {
        "status": "ok",
        "service": "quantpulse-backend"
    }
