"""
Pam Beesly Alter-ego/sub-agent 'Pamela'.
This agent is a customer support specialist who uses RAG corpus for knowledge retrieval.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from pam_beesly.pamela.config import settings  # pylint: disable=E0401
from pam_beesly.tools import list_corpora, rag_query, get_corpus_info  # pylint: disable=E0401

root_agent = LlmAgent(
    name="pamela",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[],
    tools=[
        list_corpora,
        rag_query,
        get_corpus_info,
    ],
)
