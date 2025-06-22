"""
This module holds the Agent card and skills for the Ryan Howard agent.
"""

from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)

from ryan_howard.agent import RyanHowardAgent
from ryan_howard.a2a_configs.agent_executor import RyanHowardAgentExecutor
from ryan_howard.config import agent_config

# Define agent skills and card
data_loading_skill = AgentSkill(
    id=f"{agent_config.agent_id}_data_loading",
    name="Dataset Loading and Processing",
    description="Loads and processes CSV datasets for analysis and visualization.",
    tags=["data science", "csv", "data loading", "data preparation"],
    examples=[
        "Load this CSV file for analysis",
        "Can you process my dataset from sales.csv?",
        "Show me the first few rows of the dataset",
        "Tell me about the structure of this data file",
    ],
)

data_analysis_skill = AgentSkill(
    id=f"{agent_config.agent_id}_data_analysis",
    name="Data Analysis and Statistics",
    description="Provides comprehensive statistical analysis of datasets, including summary statistics, correlation analysis, and data distribution insights.",
    tags=["data science", "statistics", "analysis", "correlations", "insights"],
    examples=[
        "What are the summary statistics for this dataset?",
        "Show me the unique values in the 'category' column",
        "Find correlations between numerical columns",
        "Analyze the distribution of ages in the dataset",
        "What are the average values across all numeric columns?",
    ],
)

data_visualization_skill = AgentSkill(
    id=f"{agent_config.agent_id}_visualization",
    name="Data Visualization",
    description="Creates various visualizations including histograms, scatter plots, box plots, pie charts, and correlation heatmaps to help understand dataset patterns and relationships.",
    tags=[
        "visualization",
        "charts",
        "graphs",
        "plots",
        "histograms",
        "scatter plots",
        "heatmaps",
    ],
    examples=[
        "Create a histogram of the age distribution",
        "Show me a scatter plot of price vs. square footage",
        "Generate a correlation heatmap for all numerical variables",
        "Make a box plot showing outliers in the revenue data",
        "Create a pie chart of customer segments",
    ],
)

data_transformation_skill = AgentSkill(
    id=f"{agent_config.agent_id}_transformation",
    name="Dataset Transformation",
    description="Transforms datasets by modifying columns, handling missing values, encoding categorical variables, and preparing data for advanced analysis.",
    tags=[
        "data transformation",
        "feature engineering",
        "encoding",
        "data cleaning",
        "preprocessing",
    ],
    examples=[
        "Can you encode the categorical columns in my dataset?",
        "Fill missing values in the sales column with the mean",
        "Drop unnecessary columns from the dataset",
        "Convert these columns to datetime format",
        "Prepare this dataset for machine learning",
    ],
)

capabilities = AgentCapabilities(
    streaming=True,
)

# Let's keep only the public agent card minimal with base skills
public_agent_card = AgentCard(
    name=agent_config.agent_name,
    description=agent_config.description,
    url=agent_config.url,
    version="1.0.0",
    defaultInputModes=RyanHowardAgent.SUPPORTED_CONTENT_TYPES,
    defaultOutputModes=RyanHowardAgent.SUPPORTED_CONTENT_TYPES,
    capabilities=capabilities,
    skills=[
        data_loading_skill,
            data_analysis_skill,
            data_visualization_skill,
            data_transformation_skill,
    ],
    #supportsAuthenticatedExtendedCard=True,
)

# Now let's have a secure agent card that includes all skills
# secure_agent_card = public_agent_card.model_copy(
#     update={
#         "name": f'{agent_config.agent_name} Extended edition',
#         "version": "1.0.1",
#         "skills": [
#             data_loading_skill,
#             data_analysis_skill,
#             data_visualization_skill,
#             data_transformation_skill,
#         ],
#     }
# )


# Create our agent executor and request handler
# For the GenAI model, you can use None if you don't need classification or specify a model
request_handler = DefaultRequestHandler(
    agent_executor=RyanHowardAgentExecutor(),
    task_store=InMemoryTaskStore(),
)
