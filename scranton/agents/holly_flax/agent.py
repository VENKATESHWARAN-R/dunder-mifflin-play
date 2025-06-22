"""
Root agent module for Holly Flax.
Holly Flax herself will handle the checking with temp agency on new recruitments.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from holly_flax.config import settings  # pylint: disable=E0401
from holly_flax.holly_the_living_breathing_angel.agent import (  # pylint: disable=E0401
    root_agent as angel_root_agent,
)


root_agent = LlmAgent(
    name="holly_flax",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[angel_root_agent],
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=settings.mcp_server_url,
                headers={
                    "X-API-Key": settings.mcp_api_key,
                }
                if settings.mcp_api_key
                else None,
                timeout=60,
            ),
            tool_filter=[
                "list_available_agents",
                "get_agent_details",
            ],
        ),
    ],
)
