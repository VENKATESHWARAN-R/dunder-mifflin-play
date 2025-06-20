"""
Main starup script for the Dunder Mifflin MCP server.
"""

import logging
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP

from dunder_mifflin_mcp.config import settings
from dunder_mifflin_mcp.tools.holly_flax.temp_agency_tools import TempAgencyTools
from dunder_mifflin_mcp.tools.holly_the_living_breathing_angel.princing_tools import (
    PricingTools,
)


# ---> Common Piece of code starts
# Configure logging
logger = logging.getLogger("dunder_mifflin_mcp")
logging.basicConfig(
    level=settings.common.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Create an MCP server with decorator syntax to avoid Tool validation issues
mcp = FastMCP(
    name=settings.common.app_name,
    host=settings.common.host,
    port=settings.common.port,
)

# <--- Common Piece of code ends


# --> Tools Initialization for Holly Flax starts
# Creating holly Flax tool instance
holly_flax_tools = TempAgencyTools(temp_agency_url=settings.holly.temp_agency_url)


# Add tools using decorator pattern
@mcp.tool()
def list_available_agents() -> Dict[str, Any]:
    """
    Get a list of all agents currently registered with the temp agency.

    Returns:
        Dict[str, Any]: Information about available agents including their
        names, specialties, and URLs.
    """
    return holly_flax_tools.list_available_agents()


@mcp.tool()
def get_agent_details(agent_url: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific agent.

    Args:
        agent_url: The URL of the agent to get details for

    Returns:
        Dict[str, Any]: Detailed information about the agent including
        name, description, capabilities, and contact info.
    """
    return holly_flax_tools.get_agent_details(agent_url)


# <--- Tools Initialization for Holly Flax ends


# --> Tools Initialization for Holly the Living Breathing Angel starts
# Creating Holly the Living Breathing Angel tool instance
angel_tools = PricingTools()


@mcp.tool()
def get_agent_hierarchy(parent_agent_name: str) -> Dict[str, Any]:
    """
    Retrieve the given agent and all its direct sub-agents.

    Args:
        parent_agent_name: The name of the parent agent to retrieve hierarchy for
    Returns:
        Dict[str, Any]: A dictionary containing the information about the agent and it's sub agents
        if any, including their names, IDs, parent agent names, models,
    """
    return angel_tools.get_agent_hierarchy(parent_agent_name)


@mcp.tool()
def get_model_pricing(model_name: str) -> Dict[str, Any]:
    """
    Retrieve pricing info for a given model.

    Args:
        model_name: The name of the model to retrieve pricing for
    Returns:
        Dict[str, Any]: A dictionary containing the model's pricing details for a specific model
        including text input and output prices, optimized purpose, and model name.
    """
    return angel_tools.get_model_pricing(model_name)


@mcp.tool()
def list_available_models() -> Dict[str, Any]:
    """
    List all currently defined models.

    Returns:
        Dict[str, Any]: A dictionary containing the information about available models
        including their names, optimized purposes, and pricing details.
    """
    return angel_tools.list_available_models()


@mcp.tool()
def compare_model_cost(
    agent_name: str, new_model: str, sample_tokens: int
) -> Dict[str, Any]:
    """
    Compare the cost of using a new model against the current model for an agent.

    Args:
        agent_name: The name of the agent to compare models for
        new_model: The name of the new model to compare against the current model
        sample_tokens: The number of tokens to use for cost comparison

    Returns:
        Dict[str, Any]: A dictionary information about the cost comparison
        including the current model, new model, and cost differences.
    """
    return angel_tools.compare_model_cost(agent_name, new_model, sample_tokens)


@mcp.tool()
def get_agent_info(agent_name: str) -> Dict[str, Any]:
    """
    Retrieve a single agent's full record by its name.

    Args:
        agent_name: The name of the agent to get details for

    Returns:
        Dict[str, Any]: Detailed information about the agent the parent agent
        name, used model, and other relevant details.
    """
    return angel_tools.get_agent_info(agent_name)


# <--- Tools Initialization for Holly the Living Breathing Angel ends


# MCP server created above with tools registered using decorators


if __name__ == "__main__":
    logger.info("Starting Dunder Mifflin MCP server")
    logger.info(
        "Server running at http://%s:%s", settings.common.host, settings.common.port
    )
    mcp.run(transport="sse")  # Start the server with SSE transport
