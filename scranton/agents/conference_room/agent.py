"""
Root agent module for the Scranton conference room.
This module initializes the root agent for the conference room, which is responsible for
managing the interactions between the sub-agents.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset

from conference_room.config import settings # pylint: disable=E0401
from creed_bratton.agent import root_agent as creed_bratton_agent # pylint: disable=E0401
from dwight_schrute.agent import root_agent as dwight_schrute_agent # pylint: disable=E0401
from holly_flax.agent import root_agent as holly_flax_agent # pylint: disable=E0401
from michael_scott.agent import root_agent as michael_scott_agent # pylint: disable=E0401
from pam_beesly.agent import root_agent as pam_beesly_agent # pylint: disable=E0401
from erin_hannon.agent import root_agent as erin_hannon_agent # pylint: disable=E0401

root_agent = LlmAgent(
    name="conference_room_orchestrator",
    model=(
        settings.model_id
        if settings.model_id.startswith("gemini")
        else LiteLlm(model=settings.model_id)
    ),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    global_instruction=settings.global_instruction,
    sub_agents=[
        creed_bratton_agent,
        dwight_schrute_agent,
        holly_flax_agent,
        michael_scott_agent,
        pam_beesly_agent,
        erin_hannon_agent,
    ],
    tools=[
        # add any conference-specific tools here
    ],
)
