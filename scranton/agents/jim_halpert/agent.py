"""
Root agent module for Jim Halpert.
Jim Halpert is the lead developer and is responsible for the application development and bug fixes.
"""

from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from jim_halpert.config import settings  # pylint: disable=E0401
from jim_halpert.big_tuna.agent import root_agent as big_tuna_root_agent  # pylint: disable=E0401
from jim_halpert.jimothy.agent import root_agent as jimothy_root_agent  # pylint: disable=E0401
from jim_halpert.golden_face.agent import root_agent as golden_face_root_agent  # pylint: disable=E0401

root_agent = LlmAgent(
    name="jim_halpert",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[big_tuna_root_agent, jimothy_root_agent, golden_face_root_agent],
    tools=[
        AgentTool(agent=golden_face_root_agent),
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[
                "get_project_tech_stack",
            ],
        ),
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=settings.github_mcp_url,
                headers={
                    "Authorization": f"Bearer {settings.github_pat_token}"
                    if settings.github_pat_token
                    else None
                },
            ),
            tool_filter=[
                "list_issues",
                "get_issue",
                "get_issue_comments",
            ],
        ),
    ],
)
