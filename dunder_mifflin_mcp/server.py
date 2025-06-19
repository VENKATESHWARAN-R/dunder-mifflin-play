"""
Main starup script for the Dunder Mifflin MCP server.
"""

import logging
from mcp.server.fastmcp import FastMCP

from dunder_mifflin_mcp.config import settings
from dunder_mifflin_mcp.tools.holly_flax.temp_agency_tools import TempAgencyTools

# Configure logging
logger = logging.getLogger("dunder_mifflin_mcp")
logging.basicConfig(
    level=settings.common.log_level.upper(),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Creating holly Flax tool instance
holly_flax = TempAgencyTools(temp_agency_url=settings.holly.temp_agency_url)

# Create an MCP server with decorator syntax to avoid Tool validation issues
mcp = FastMCP(
    name=settings.common.app_name,
    host=settings.common.host,
    port=settings.common.port,
)


# Add tools using decorator pattern
@mcp.tool()
def list_available_agents():
    """
    Get a list of all agents currently registered with the temp agency.

    Returns:
        Dict[str, Any]: Information about available agents including their
        names, specialties, and URLs.
    """
    return holly_flax.list_available_agents()


@mcp.tool()
def get_agent_details(agent_url: str):
    """
    Get detailed information about a specific agent.

    Args:
        agent_url: The URL of the agent to get details for

    Returns:
        Dict[str, Any]: Detailed information about the agent including
        name, description, capabilities, and contact info.
    """
    return holly_flax.get_agent_details(agent_url)


# MCP server created above with tools registered using decorators


if __name__ == "__main__":
    logger.info("Starting Dunder Mifflin MCP server")
    logger.info(
        "Server running at http://%s:%s", settings.common.host, settings.common.port
    )
    mcp.run(transport="sse")  # Start the server with SSE transport
