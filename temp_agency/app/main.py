"""
Main module for the Dunder Mifflin Temp Agency service.
"""

import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI

from app.api import api_router
from app.api.health import http_client_dependency
from app.config import settings
# from app.db.mongodb import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("temp-agency")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing Temp Agency service...")

    # Initialize HTTP client
    http_client_dependency.client = httpx.AsyncClient()

    logger.info("Temp Agency service initialization complete")
    yield

    # Shutdown
    logger.info("Shutting down Temp Agency service...")

    # Close HTTP client
    if http_client_dependency.client:
        await http_client_dependency.client.aclose()
        logger.info("HTTP client closed")

    logger.info("Temp Agency service shutdown complete")


def create_application() -> FastAPI:
    """
    Creates and configures the FastAPI application.

    Returns:
        A configured FastAPI application
    """
    app = FastAPI(
        title="Dunder Mifflin Temp Agency",
        description="A service for registering and discovering freelance agents",
        version="0.1.0",
        lifespan=lifespan,
    )

    # Include API router
    app.include_router(api_router)

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting Dunder Mifflin Temp Agency service...")
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        log_level=settings.LOG_LEVEL,
        lifespan="on",
        reload=settings.RELOAD,
        workers=settings.WORKERS,
    )
    logger.info("Dunder Mifflin Temp Agency service started successfully.")
