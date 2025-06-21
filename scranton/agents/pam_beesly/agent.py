"""
Root agent module for Pam Beesly.
Pam Beesly is the support engineer and is responsible for handling customer queries and issues.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from pam_beesly.config import settings  # pylint: disable=E0401
from pam_beesly.pamela.agent import root_agent as pamela_root_agent  # pylint: disable=E0401
from pam_beesly.pam_casso.agent import root_agent as pam_casso_root_agent  # pylint: disable=E0401
from pam_beesly.pam_cake.agent import root_agent as pam_cake_root_agent  # pylint: disable=E0401

root_agent = LlmAgent(
    name="pam_beesly",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[pamela_root_agent, pam_casso_root_agent, pam_cake_root_agent],
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[
                "get_application_info",
                "get_feature_info"
            ],
        )
    ],
)
