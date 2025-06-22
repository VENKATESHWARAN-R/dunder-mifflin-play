"""
Pam Beesly Alter-ego/sub-agent 'Pam Casso'.
This agent creates summaries of conversations and can store them in the RAG corpus.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StreamableHTTPConnectionParams

from pam_beesly.pam_casso.config import settings  # pylint: disable=E0401

root_agent = LlmAgent(
    name="pam_casso",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[],
    tools=[
        MCPToolset(
            connection_params=StreamableHTTPConnectionParams(
                url=settings.mcp_server_url,
                timeout=60,
            ),
            tool_filter=[
                "add_summary_to_rag_corpus",
                "get_summary_from_rag_corpus"
            ],
        )
    ],
)
