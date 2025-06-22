"""
Michael Scott Alter-ego/sub-agent 'Prison Mike'.
This agent handles conference room meetings and ensures the team stays focused.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from michael_scott.prison_mike.config import settings  # pylint: disable=E0401

root_agent = LlmAgent(
    name="prison_mike",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[],
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[],
        )
    ],
)
