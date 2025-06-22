"""
Root agent module for Erin Hannon.
Erin Hannon is the test engineer responsible for testing the application for bugs.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from erin_hannon.config import settings  # pylint: disable=E0401

root_agent = LlmAgent(
    name="erin_hannon",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[],
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
                "list_pull_requests",
                "get_pull_request",
                "get_pull_request_files",
                "get_pull_request_diff",
                "get_pull_request_reviews",
                "get_pull_request_comments",
                "add_pull_request_review_comment_to_pending_review",
                "submit_pending_pull_request_review",
            ]
        ),
    ],
)
