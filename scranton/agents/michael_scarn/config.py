"""
Configuration for the Michael Scarn agent.
"""

import os
from dataclasses import dataclass, field
from google.adk.agents.readonly_context import ReadonlyContext
from dotenv import load_dotenv

from michael_scarn.prompts import (  # pylint: disable=E0401
    get_agent_instruction,
    get_agent_description,
)

load_dotenv()


@dataclass
class AgentConfig:
    """
    Configuration for the agent.
    """

    # --> Common settings
    database_url: str | None = field(
        default_factory=lambda: os.getenv("DATABASE_URL", None)
    )
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    # <-- End of common settings

    # --> Agent specific settings
    @staticmethod
    def agent_instruction(context: ReadonlyContext) -> str:
        return get_agent_instruction(os.getenv("MICHAEL_SCARN_INSTRUCTION_VERSION", "v1"))

    @property
    def agent_description(self) -> str:
        return get_agent_description(os.getenv("MICHAEL_SCARN_DESCRIPTION_VERSION", "v1"))

    model_id: str = field(
        default_factory=lambda: os.getenv("MICHAEL_SCARN_MODEL_ID", "gemini-2.0-flash")
    )
    # <-- End of agent specific settings


settings = AgentConfig()
