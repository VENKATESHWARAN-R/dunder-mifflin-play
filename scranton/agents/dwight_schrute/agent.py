"""
Root agent module for Dwight Schrute
Dwight Schrute is a Database administrator
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from dwight_schrute.config import settings  # pylint: disable=E0401
from dwight_schrute.tools.db_tools import DatabaseTools  # pylint: disable=E0401


database_tool_set = DatabaseTools(
    database_url=settings.app_database_url,
)

root_agent = LlmAgent(
    name="dwight_schrute",
    model=settings.model_id
    if settings.model_id.startswith("gemini")
    else LiteLlm(model=settings.model_id),
    description=settings.agent_description,
    instruction=settings.agent_instruction,
    tools=[
        database_tool_set.get_schema_description,
        database_tool_set.get_user_by_username,
        database_tool_set.get_user_by_email,
        database_tool_set.count_users,
        database_tool_set.get_subscription_pricing,
        database_tool_set.count_subscriptions_by_status,
        database_tool_set.sum_revenue,
        database_tool_set.compare_revenue,
        database_tool_set.calculate_mrr,
        database_tool_set.calculate_churn_rate,
    ],
)
