"""
Configuration settings for the Temp Agency service.
"""

import os

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Configuration settings for the application."""

    # Database Configuration
    DATABASE_URL = os.getenv("DATABASE_URL", "")

    # Server Configuration
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "6000"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "info")
    RELOAD: bool = os.getenv("RELOAD", "False").lower() == "true"
    WORKERS: int = int(os.getenv("WORKERS", "1"))

    # Application Settings
    PUBLIC_AGENT_CARD_PATH: str = os.getenv(
        "PUBLIC_AGENT_CARD_PATH", "/.well-known/agent.json"
    )


settings = Settings()
