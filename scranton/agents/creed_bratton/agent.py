"""
Root agent module for Creed Bratton.
Creed Bratton is a security specialist responsible for application security and vulnerability detection.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from creed_bratton.config import settings  # pylint: disable=E0401
from creed_bratton.william_charles_schneider.agent import root_agent as william_schneider_root_agent  # pylint: disable=E0401

root_agent = LlmAgent(
    name="creed_bratton",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[william_schneider_root_agent],
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[
                "get_vulnerability_report", 
                "get_security_audit_report",
                "github_mcp_server",
                "google_search"
            ],
        )
    ],
)
