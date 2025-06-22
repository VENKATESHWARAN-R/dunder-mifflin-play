"""
Pam Beesly Alter-ego/sub-agent 'Pam Casso'.
This agent creates summaries of conversations and can store them in the RAG corpus.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from pam_beesly.pam_casso.config import settings  # pylint: disable=E0401
from pam_beesly.tools import add_content_to_corpus, list_corpora, get_corpus_info  # pylint: disable=E0401

root_agent = LlmAgent(
    name="pam_casso",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    sub_agents=[],
    tools=[
        add_content_to_corpus,
        list_corpora,
        get_corpus_info,
    ],
)
