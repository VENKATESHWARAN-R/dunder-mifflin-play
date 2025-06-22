"""
Jim Halpert Alter-ego/sub-agent 'Big Tuna'.
This agent is a Full stack specialist who handles application development.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from jim_halpert.big_tuna.config import settings  # pylint: disable=E0401
from jim_halpert.golden_face.agent import root_agent as golden_face_root_agent  # pylint: disable=E0401

root_agent = LlmAgent(
    name="big_tuna",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[golden_face_root_agent],
    tools=[
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
                "get_file_contents",
                "create_or_update_file",
                "list_branches",
                "create_branch",
                "list_commits",
                "get_commit",
                "search_code",
            ],
        ),
    ],
)
