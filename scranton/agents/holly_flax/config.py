"""
Configs module for Holly Flax agent.
"""

import os
from dataclasses import dataclass, field
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
    agent_runtime_config: RunConfig = field(
        default_factory=lambda: RunConfig(
            streaming_mode=StreamingMode.SSE
            if os.getenv("STREAMING_MODE", "").upper() == "SSE"
            else StreamingMode.NONE,
            max_llm_calls=int(
                os.getenv("MAX_LLM_CALLS", "25")
            ),  # This defines the maximum number of LLM calls the agent can make in single inference
        )
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
