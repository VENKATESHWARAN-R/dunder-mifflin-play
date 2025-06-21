"""
Pam Beesly Alter-ego/sub-agent 'Pamela'.
This agent is a customer support specialist who uses RAG corpus for knowledge retrieval.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from pam_beesly.pamela.config import settings  # pylint: disable=E0401

root_agent = LlmAgent(
    name="pamela",
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
                "get_rag_corpus",
                "answer_customer_query_using_rag"
            ],
        )
    ],
)
