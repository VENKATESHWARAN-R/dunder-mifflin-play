"""
Configuration module which loads the env vars and sets up the application configs.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()


@dataclass
class CommonConfig:
    """
    Common configuration settings shared across all components
    """

    app_name: str = field(
        default_factory=lambda: os.getenv("APP_NAME", "Dunder_Mifflin_Play")
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    host: str = field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = field(default_factory=lambda: int(os.getenv("PORT", "8080")))
    agents_database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/yourdb")
    )


@dataclass
class HollyConfig:
    """
    Configuration for Holly Flax
    """

    temp_agency_url: str = field(
        default_factory=lambda: os.getenv("TEMP_AGENCY_URL", "http://localhost:8000")
    )
    database_url: str = field(
        default_factory=lambda: os.getenv("DATABASE_URL", "postgresql+psycopg2://user:pass@localhost:5432/yourdb")
    )


@dataclass
class JimConfig:
    """
    Configuration for Jim Halpert
    """

    database_url: str | None = field(
        default_factory=lambda: os.getenv("DATABASE_URL", None)
    )


@dataclass
class MichaelConfig:
    """
    Configuration for Michael Scott
    """

    database_url: str | None = field(
        default_factory=lambda: os.getenv("DATABASE_URL", None)
    )


@dataclass
class Settings:
    """
    Main settings class that combines all configuration components
    """

    common: CommonConfig = field(default_factory=CommonConfig)
    holly: HollyConfig = field(default_factory=HollyConfig)
    jim: JimConfig = field(default_factory=JimConfig)
    michael: MichaelConfig = field(default_factory=MichaelConfig)

    @classmethod
    def get_settings(cls) -> "Settings":
        """
        Factory method to create and return a Settings instance.
        This allows for singleton-like behavior if needed.
        """
        return cls()


# Create a default settings instance for easy import
settings = Settings.get_settings()

# To access the settings we can use:
# from dunder_mifflin_mcp.config import settings
# settings.common.app_name
# settings.holly.temp_agency_url
