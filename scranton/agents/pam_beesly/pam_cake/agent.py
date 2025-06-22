"""
Pam Beesly Alter-ego/sub-agent 'Pam Cake'.
This agent holds technical details about the application architecture and team contact points.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from pam_beesly.pam_cake.config import settings  # pylint: disable=E0401

root_agent = LlmAgent(
    name="pam_cake",
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
            tool_filter=[
                "get_application_architecture",
                "get_application_design",
                "get_implementation_details",
                "get_contact_points"
            ],
        )
    ],
)
