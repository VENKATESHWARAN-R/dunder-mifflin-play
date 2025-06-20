"""
Holly Flax Alter-ego/sub-agent 'The living breathing angel'.
This agent specializes in tracking team member models, pricing details, and financial projections.
"""

import logging

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

try:
    from scranton.agents.holly_flax.holly_the_living_breathing_angel.config import settings
except ImportError as e:
    # Fallback import if the config module is not found
    from .config import settings


logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level.upper())

root_agent = LlmAgent(
    name="holly_the_living_breathing_angel",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[],
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[
                "get_agent_hierarchy",
                "get_model_pricing",
                "list_available_models",
                "compare_model_cost",
                "get_agent_info",
            ],
        )
    ],
)
