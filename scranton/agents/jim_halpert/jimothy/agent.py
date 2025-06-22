"""
Jim Halpert Alter-ego/sub-agent 'Jimothy'.
This agent is an operations specialist focused on GitHub workflows and deployment.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from jim_halpert.jimothy.config import settings  # pylint: disable=E0401

root_agent = LlmAgent(
    name="jimothy",
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
                "list_workflows",
                "list_workflow_runs",
                "get_workflow_run",
                "get_workflow_run_logs",
                "rerun_workflow_run",
                "rerun_failed_jobs",
                "cancel_workflow_run",
            ],
        ),
    ],
)
