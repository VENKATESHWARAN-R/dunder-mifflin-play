from google.adk.agents import LlmAgent
from .prison_mike.agent import (
    root_agent as prison_mike_agent,
)
from .date_mike.agent import root_agent as date_mike_agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, SseServerParams

from dotenv import load_dotenv

load_dotenv()


AGEN_DESCRIPTION = (
    """Root agent coordinating tasks and delegating to specialized child agents."""
)
AGENT_INSTRUCTION = """
You are Michael Scott, the enthusiastic and quirky regional manager who coordinates tasks efficiently by delegating to your specialized agents.  
Your role is to understand the user's request, decide which child agent (Prison Mike or Date Mike) is best suited, and forward the task clearly.  
Respond with confidence and a positive tone, adding a touch of humor if appropriate, but keep responses concise and focused on delegation.  
Avoid giving detailed answers yourself unless no child agent fits the task.

you also have tool to check new hires in the Dunder Mifflin temp agency.
use it appropriately to find the right agent for the task at hand.
"""


root_agent = LlmAgent(
    name="michael_scott",
    model="gemini-2.0-flash-001",
    description=AGEN_DESCRIPTION,
    instruction=AGENT_INSTRUCTION,
    sub_agents=[prison_mike_agent, date_mike_agent],
    tools=[
        MCPToolset(
            connection_params=SseServerParams(
                url="https://dunder-mifflin-mcp-server-852224482282.europe-north1.run.app/sse",
                timeout=60,
            ),
        )
    ],
)
