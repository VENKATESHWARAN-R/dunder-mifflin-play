"""
Root agent module for Ryan Howard.
Ryan Howard is a freelance data scientist available through the temp agency.
"""

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams

from ryan_howard.config import settings  # pylint: disable=E0401

root_agent = LlmAgent(
    name="ryan_howard",
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
                "load_csv",
                "get_basic_info",
                "get_summary_statistics",
                "plot_histograms",
                "get_unique_values",
                "get_data_sample",
                "create_boxplot",
                "create_scatter_plot",
                "plot_correlation_heatmap",
                "plot_pie_chart",
                "modify_dataset",
                "encode_categorical_columns",
                "read_from_gcs",
                "write_to_gcs"
            ],
        )
    ],
)
