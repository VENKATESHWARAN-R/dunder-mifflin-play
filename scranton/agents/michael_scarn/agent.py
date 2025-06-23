"""
Michael Scarn Agent Configuration
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.agent_tool import AgentTool

from michael_scarn.config import settings  # pylint: disable=E0401
from creed_bratton.agent import root_agent as creed_bratton_agent  # pylint: disable=E0401
from dwight_schrute.agent import root_agent as dwight_schrute_agent  # pylint: disable=E0401
from holly_flax.agent import root_agent as holly_flax_agent  # pylint: disable=E0401
from michael_scott.agent import root_agent as michael_scott_agent  # pylint: disable=E0401
from pam_beesly.agent import root_agent as pam_beesly_agent  # pylint: disable=E0401
from erin_hannon.agent import root_agent as erin_hannon_agent  # pylint: disable=E0401

root_agent = LlmAgent(
    name="michael_scarn",
    model=(
        settings.model_id
        if settings.model_id.startswith("gemini")
        else LiteLlm(model=settings.model_id)
    ),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    tools=[
        AgentTool(creed_bratton_agent),
        AgentTool(dwight_schrute_agent),
        AgentTool(holly_flax_agent),
        AgentTool(michael_scott_agent),
        AgentTool(pam_beesly_agent),
        AgentTool(erin_hannon_agent),
    ],
)
