"""
This is just a dict module for the agent configuration.
"""

from typing import Dict, Any
from scranton.agents.holly_flax.agent import root_agent as holly_flax_agent

AGENTS_CONFIG: Dict[str, Any] = {
    "agents": {
        "holly_flax": {
            "agent": holly_flax_agent,
            "display_name": "Holly Flax",
            "description": "Human Resources Representative",
            "gcs_dir_name": "holly_flax",
            "requirements": "scranton/agents/holly_flax/requirements.txt",
            "env_vars": {
                "LOG_LEVEL": "INFO",
                "DATABASE_URL": {"secret": "agents-db-url", "version": "latest"},
                "MCP_SERVER_URL": {"secret": "mcp-server-url", "version": "latest"},
                "HOLLY_INSTRUCTION_VERSION": "v1",
                "HOLLY_DESCRIPTION_VERSION": "v1",
                "ANGEL_INSTRUCTION_VERSION": "v1",
                "ANGEL_DESCRIPTION_VERSION": "v1",
                "HOLLY_MODEL_ID": "gemini-2.0-flash-lite",
                "ANGEL_MODEL_ID": "gemini-2.0-flash-lite",
            },
        }
    }
}
