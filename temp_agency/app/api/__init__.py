"""
API routes for the Temp Agency service.
"""

from fastapi import APIRouter

from app.api.agents import router as agents_router
from app.api.health import router as health_router

# Create main API router
api_router = APIRouter()

# Include sub-routers
api_router.include_router(agents_router, tags=["agents"])
api_router.include_router(health_router, tags=["health"])
