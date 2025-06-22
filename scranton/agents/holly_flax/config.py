"""
Configs module for Holly Flax agent.
"""

import os
from dataclasses import dataclass, field
from google.adk.agents.readonly_context import ReadonlyContext
from dotenv import load_dotenv

from google.adk.agents.run_config import RunConfig, StreamingMode

from holly_flax.prompts import (  # pylint: disable=E0401
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

    mcp_server_url: str = field(
        default_factory=lambda: os.getenv("MCP_SERVER_URL", "http://localhost:8080/sse")
    )
    mcp_api_key: str | None = field(
        default_factory=lambda: os.getenv("MCP_API_KEY", None)
    )
    github_pat_token: str | None = field(
        default_factory=lambda: os.getenv("GITHUB_PAT_TOKEN", None)
    )
    github_mcp_url: str = field(
        default_factory=lambda: os.getenv("GITHUB_MCP_URL", "https://api.githubcopilot.com/mcp/")
    )
    # <-- End of common settings

    # --> Agent specific settings
    @staticmethod
    def agent_instruction(context: ReadonlyContext) -> str:
        return get_agent_instruction(
            os.getenv("HOLLY_INSTRUCTION_VERSION", "v1")
        )
    @property
    def agent_description(self) -> str:
        return get_agent_description(
            os.getenv("HOLLY_DESCRIPTION_VERSION", "v1")
        )
    model_id: str = field(
        default_factory=lambda: os.getenv("HOLLY_MODEL_ID", "gemini-2.0-flash-lite")
    )
    # <-- End of agent specific settings


settings = AgentConfig()
