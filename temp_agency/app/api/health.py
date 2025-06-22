"""
Health check endpoints for the Temp Agency service.
"""

from fastapi import APIRouter, Depends, HTTPException

import httpx
from sqlalchemy import text
from app.db.postgres import SessionLocal, engine
from app.models.models import HealthCheckResponse

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(http_client: httpx.AsyncClient = Depends(lambda: getattr(http_client_dependency, "client", None))):
    """
    Check the health of the temp-agency service.
    
    Returns:
        A HealthCheckResponse indicating the service health status
    """
    # Default health status
    health = {
        "status": "healthy",
        "postgres_connected": False,
        "http_client_available": http_client is not None,
    }
    
    # Check PostgreSQL connection
    db_connection = None
    try:
        db_connection = SessionLocal()
        # Execute a simple query to verify the connection
        db_connection.execute(text("SELECT 1"))
        health["postgres_connected"] = True
    except Exception as e:
        health["status"] = "degraded"
        health["details"] = f"PostgreSQL connection not available: {str(e)}"
    finally:
        if db_connection:
            db_connection.close()
    
    if not http_client:
        health["status"] = "degraded"
        if "details" in health:
            health["details"] += "; HTTP client not available"
        else:
            health["details"] = "HTTP client not available"
            
    return health


# This will be set in the main application during startup
class HttpClientDependency:
    """Dependency for httpx client."""
    client: httpx.AsyncClient = None


http_client_dependency = HttpClientDependency()
