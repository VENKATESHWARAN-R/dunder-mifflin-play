"""
Michael Scott Alter-ego/sub-agent 'Michael Scarn'.
This agent is a project management specialist who can delegate tasks and work with other team members.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from michael_scott.michael_scarn.config import settings  # pylint: disable=E0401
from michael_scott.michael_the_magic.agent import root_agent as michael_the_magic_root_agent  # pylint: disable=E0401

root_agent = LlmAgent(
    name="michael_scarn",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[michael_the_magic_root_agent],
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[
                "get_current_task_state",
                "update_task_state",
                "get_task_status", 
                "send_a2a_message"
            ],
        )
    ],
)
