"""
Tools for Holly Flax agent to communicate with the temp agency.
"""

import logging
from typing import Dict, Any

import httpx

logger = logging.getLogger("holly-flax-tools")


class TempAgencyTools:
    """
    Tools for interacting with the temp agency API.
    Holly uses these tools to find suitable agents for various tasks.
    """

    def __init__(self, temp_agency_url: str):
        """Initialize the temp agency tools with the API endpoint.

        Args:
            temp_agency_url (str): The base URL of the temp agency API.
        """
        self.temp_agency_url = temp_agency_url
        self.client = httpx.Client(timeout=10.0)

    def list_available_agents(self) -> Dict[str, Any]:
        """
        Get a list of all agents currently registered with the temp agency.

        Returns:
            Dict[str, Any]: Information about available agents including their
            names, specialties, and URLs.
        """
        try:
            response = self.client.get(f"{self.temp_agency_url}/agents/")
            response.raise_for_status()
            agents = response.json()

            result = {
                "status": "success",
                "message": f"Found {len(agents.get('agents', []))} agents",
                "agents": agents.get("agents", []),
            }

            # Format the response for better readability
            if result["agents"]:
                agent_info = []
                for agent in result["agents"]:
                    agent_info.append(
                        {
                            "name": agent.get("name", "Unknown"),
                            "description": agent.get(
                                "description", "No description available"
                            ),
                            "url": agent.get("url", ""),
                        }
                    )
                result["agents"] = agent_info

            return result
        except Exception as e:
            logger.error(f"Error listing agents: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve agents: {str(e)}",
            }

    def get_agent_details(self, agent_url: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific agent.

        Args:
            agent_url: The URL of the agent to get details for

        Returns:
            Dict[str, Any]: Detailed information about the agent including
            name, description, capabilities, and contact info.
        """
        if not agent_url:
            return {"status": "error", "message": "Agent URL is required"}

        try:
            response = self.client.get(
                f"{self.temp_agency_url}/agents/by-url",
                params={"url": agent_url},
            )
            response.raise_for_status()
            agent_details = response.json()

            return {"status": "success", "agent": agent_details}
        except Exception as e:
            logger.error(f"Error getting agent details for {agent_url}: {str(e)}")
            return {
                "status": "error",
                "message": f"Failed to retrieve agent details: {str(e)}",
            }
