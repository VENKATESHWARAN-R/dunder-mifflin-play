"""
Root agent module for Jim Halpert.
Jim Halpert is the lead developer and is responsible for the application development and bug fixes.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from jim_halpert.config import settings  # pylint: disable=E0401
from jim_halpert.big_tuna.agent import root_agent as big_tuna_root_agent  # pylint: disable=E0401
from jim_halpert.jimothy.agent import root_agent as jimothy_root_agent  # pylint: disable=E0401

root_agent = LlmAgent(
    name="jim_halpert",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[big_tuna_root_agent, jimothy_root_agent],
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[
                "get_current_tech_stack", 
                "google_search",
                "get_github_issues",
                "get_github_notifications"
            ],
        )
    ],
)
