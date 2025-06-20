"""
Configs module for Holly Flax agent.
"""

import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

try:
    from scranton.agents.holly_flax.prompts import (
        get_agent_instruction,
        get_agent_description,
    )
except ImportError as e:
    # Fallback import if the prompts module is not found
    from .prompts import get_agent_instruction, get_agent_description
# from scranton.agents.holly_flax.prompts import (
#     get_agent_instruction,
#     get_agent_description,
# )

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

    mcp_server_url: str = field(
        default_factory=lambda: os.getenv("MCP_SERVER_URL", "http://localhost:8080/sse")
    )
    # <-- End of common settings

    # --> Agent specific settings
    agent_instruction: str = field(
        default_factory=lambda: get_agent_instruction(
            os.getenv("HOLLY_INSTRUCTION_VERSION", "v1")
        )
    )
    agent_description: str = field(
        default_factory=lambda: get_agent_description(
            os.getenv("HOLLY_DESCRIPTION_VERSION", "v1")
        )
    )
    model_id: str = field(
        default_factory=lambda: os.getenv("HOLLY_MODEL_ID", "gemini-2.0-flash-lite")
    )
    # <-- End of agent specific settings

settings = AgentConfig()
