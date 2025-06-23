"""
Root agent module for Michael Scott.
Michael Scott is the project manager who oversees the project.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from michael_scott.config import settings  # pylint: disable=E0401

# from michael_scott.prison_mike.agent import (  # pylint: disable=E0401
#     root_agent as prison_mike_root_agent,
# )
from michael_scott.date_mike.agent import (  # pylint: disable=E0401
    root_agent as date_mike_root_agent,
)
from michael_scott.michael_the_magic.agent import (  # pylint: disable=E0401
    root_agent as michael_the_magic_root_agent,
)

# from michael_scott.michael_scarn.agent import (  # pylint: disable=E0401
#     root_agent as michael_scarn_root_agent,
# )
from michael_scott.a2a_communication.a2a_client import (
    fetch_agent_card,
    send_message_to_agent,
)


root_agent = LlmAgent(
    name="michael_scott",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[date_mike_root_agent, michael_the_magic_root_agent],
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[
                "get_project_tech_stack",
                "get_application_architecture",
            ],
        ),
        fetch_agent_card,
        send_message_to_agent,
    ],
)
