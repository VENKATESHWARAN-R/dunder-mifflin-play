"""
Ryan Howard Agent A2A Application
This is the main entry point for the Ryan Howard agent,
which registers with an agency and provides data analysis capabilities.

For running this A2A server, go to the parent directory of this file and run:
uvicorn ryan_howard.a2a_server:app --host localhost --port 10010 --reload
"""

import logging
import asyncio
from typing import Any, Dict
from contextlib import asynccontextmanager

from a2a.server.apps.jsonrpc import A2AFastAPIApplication
from fastapi import FastAPI
import httpx

from ryan_howard.a2a_configs.agent_a2a_configs import (
    public_agent_card,
    request_handler,
)
from ryan_howard.authentication.auth import RyanHowardAuthMiddleware
from ryan_howard.config import agent_config
# from dunder_mifflin_shared.agency import (
#     register_to_agency,
#     deregister_from_agency,
# )

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("google_adk.google.adk.models.registry").setLevel(logging.WARNING)
logging.getLogger("matplotlib.font_manager").setLevel(logging.WARNING)
logger = logging.getLogger("ryan-howard-agent")

# Closure to store the registered state
# This is for non-employee agents only
is_registered = {"value": False}


async def register_to_agency(
    agent_service_url: str, temp_agency_url: str
) -> Dict[str, Any]:
    """Registers the agent to the agency and returns the response from Agency.

    Args:
        agent_service_url (str): The URL of the agent to be registered.
        temp_agency_url (str): The URL of the temporary agency to register with.

    Returns:
        Dict[str, Any]: The response from the agency containing registration details.
    """
    for attempt in range(1, 4):  # 3 attempts
        try:
            logger.info(
                "Making registration request (attempt %d/3) to %s/register_agent/",
                attempt,
                temp_agency_url,
            )
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{temp_agency_url}/register_agent/",
                    json={"agent_service_url": agent_service_url},
                    timeout=10.0,
                )

                if response.status_code == 200:
                    logger.info("Registration successful")
                    return response.json()
                else:
                    logger.warning(
                        "Registration failed with status code: %s", response.status_code
                    )
        except Exception as e:
            logger.warning("Registration attempt %d failed: %s", attempt, str(e))
            if attempt == 3:
                return {
                    "status": "error",
                    "message": f"Failed after 3 attempts: {str(e)}",
                }

            await asyncio.sleep(2)

    return {"status": "error", "message": "Registration failed after 3 attempts"}


async def deregister_from_agency(
    agent_service_url: str, temp_agency_url: str
) -> Dict[str, Any]:
    """Deregisters the agent from the agency and returns the response from Agency.

    Args:
        agent_service_url (str): The URL of the agent to be deregistered.
        temp_agency_url (str): The URL of the temporary agency to deregister from.

    Returns:
        Dict[str, Any]: The response from the agency confirming deregistration.
    """
    try:
        logger.info(
            "Making deregistration request to %s/deregister_agent/by-url",
            temp_agency_url,
        )
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{temp_agency_url}/deregister_agent/by-url",
                params={"url": agent_service_url},
                timeout=10.0,
            )

            if response.status_code == 200:
                logger.info("Deregistration successful")
                return response.json()
            else:
                logger.warning(
                    "Deregistration failed with status code: %s", response.status_code
                )
                return {
                    "status": "error",
                    "message": f"Failed with status code: {response.status_code}",
                }
    except Exception as e:
        logger.warning("Failed to deregister agent: %s", str(e))
        return {"status": "error", "message": str(e)}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    This handles the startup and shutdown logic for the agent,
    including registration with the agency.
    and deregistration when the application stops.
    """
    # --- Startup Logic ---
    logger.info(
        "Agent starting up... Will register with agency after server is fully running"
    )

    async def delayed_registration():
        await asyncio.sleep(5)  # Wait 5 seconds for server readiness
        agent_url = agent_config.url
        logger.info(
            "Registering agent at %s with agency at %s",
            agent_url,
            agent_config.temp_agency_url,
        )
        try:
            result = await register_to_agency(agent_url, agent_config.temp_agency_url)
            if result.get("status") != "error":
                is_registered["value"] = True
                logger.info("Agent successfully registered with agency")
            else:
                logger.warning("Failed to register with agency")
        except Exception as e:
            logger.error("Error during registration: %s", str(e))

    # Kick off the background registration task
    asyncio.create_task(delayed_registration())

    # Yield control: application starts serving requests after this
    yield

    # --- Shutdown Logic ---
    if is_registered["value"]:
        agent_url = agent_config.url
        logger.info("Deregistering agent at %s from agency", agent_url)
        try:
            result = await deregister_from_agency(
                agent_url, agent_config.temp_agency_url
            )
            logger.info("Agent deregistered from agency: %s", result)
        except Exception as e:
            logger.error("Error during deregistration: %s", str(e))


# Create A2A application
server = A2AFastAPIApplication(
    agent_card=public_agent_card,
    http_handler=request_handler,
)

# Build the ASGI app
app = server.build(lifespan=lifespan)

# Adding middleware for authentication if creds are available
logger.info("Configuring Ryan Howard agent A2A server...")
if agent_config.secure_agent or agent_config.users or agent_config.api_keys:
    logger.info("Adding authentication middleware to the Ryan Howard agent")
    app.add_middleware(RyanHowardAuthMiddleware)

if __name__ == "__main__":
    import signal
    import uvicorn

    # Handle graceful shutdown on CTRL+C
    def shutdown_handler(signum, frame):
        logger.info("Received shutdown signal. Exiting gracefully...")
        raise KeyboardInterrupt()

    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)

    # Run the server
    logger.info(
        "Starting Ryan Howard agent on %s:%s", agent_config.host, agent_config.port
    )
    uvicorn.run(app, host="0.0.0.0", port=int(agent_config.port))
