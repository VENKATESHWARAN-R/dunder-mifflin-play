"""
Michael Scott Alter-ego/sub-agent 'Michael The Magic'.
This agent is a specialist in breaking down tasks logically and assigning them appropriately.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from michael_scott.michael_the_magic.config import settings  # pylint: disable=E0401

root_agent = LlmAgent(
    name="michael_the_magic",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[],
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[
                "get_agents_info",
            ],
        )
    ],
)
