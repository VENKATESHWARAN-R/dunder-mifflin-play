"""
Creed Bratton Alter-ego/sub-agent 'William Charles Schneider'.
This agent is a security specialist who handles security audits and vulnerability scans.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from creed_bratton.william_charles_schneider.config import settings  # pylint: disable=E0401

root_agent = LlmAgent(
    name="william_charles_schneider",
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
                headers={
                    "X-API-Key": settings.mcp_api_key,
                }
                if settings.mcp_api_key
                else None,
                timeout=60,
            ),
            tool_filter=["run_pen_test", "run_vulnerability_scan"],
        )
    ],
)
