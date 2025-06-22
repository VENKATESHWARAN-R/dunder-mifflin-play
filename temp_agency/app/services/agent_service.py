"""
Services for Temp Agency application.
"""

import logging
import time
from typing import Dict, Optional

import httpx
from a2a.client import A2ACardResolver
from a2a.types import AgentCard

from app.config import settings

logger = logging.getLogger("temp-agency")


class AgentService:
    """Service for handling agent-related operations."""
    
    @staticmethod
    async def fetch_public_agent_card(
        agent_base_url: str, httpx_client: httpx.AsyncClient
    ) -> Optional[AgentCard]:
        """
        Fetches the public agent card using A2ACardResolver.
        
        Args:
            agent_base_url: The base URL of the agent
            httpx_client: HTTP client for making the request
            
        Returns:
            An AgentCard object if successful, None otherwise
        """
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=agent_base_url,
        )
        try:
            logger.info(
                f"Temp-Agency: Attempting to fetch public agent card from: {agent_base_url}{resolver.agent_card_path}"
            )
            public_card = await resolver.get_agent_card()
            logger.info(
                f"Temp-Agency: Successfully fetched public agent card for {agent_base_url}"
            )
            return public_card
        except Exception as e:
            logger.error(
                f"Temp-Agency: Error fetching public agent card from {agent_base_url}: {e}",
                exc_info=True,
            )
            return None
    
    @staticmethod
    async def check_agent_health(agent_url: str, httpx_client: httpx.AsyncClient) -> Dict:
        """
        Check if an agent is online by attempting to access its public agent card.
        
        Args:
            agent_url: The base URL of the agent
            httpx_client: HTTP client for making the request
            
        Returns:
            A dictionary containing health status information
        """
        health_info = {"is_online": False, "last_checked": None, "response_time_ms": None}

        try:
            start_time = time.time()

            # Attempt to fetch the agent's card
            card = await AgentService.fetch_public_agent_card(agent_url, httpx_client)

            end_time = time.time()
            response_time_ms = round((end_time - start_time) * 1000, 2)

            health_info["is_online"] = card is not None
            health_info["last_checked"] = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC", time.gmtime()
            )
            health_info["response_time_ms"] = response_time_ms

            logger.info(
                f"Temp-Agency: Agent health check for {agent_url}: {'Online' if health_info['is_online'] else 'Offline'}"
            )

        except Exception as e:
            logger.error(
                f"Temp-Agency: Error checking agent health for {agent_url}: {e}",
                exc_info=True,
            )
            health_info["is_online"] = False
            health_info["last_checked"] = time.strftime(
                "%Y-%m-%d %H:%M:%S UTC", time.gmtime()
            )

        return health_info
