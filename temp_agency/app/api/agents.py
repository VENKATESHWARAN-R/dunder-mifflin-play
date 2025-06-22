"""
Agent management API endpoints for the Temp Agency service.
"""

import logging
import os
from datetime import datetime

from fastapi import APIRouter, Body, Depends, HTTPException, Query
import httpx
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import (
    Agent,
    AgentRegistrationResponse,
    AgentDeregistrationResponse,
    AgentListResponse,
)
from app.services.agent_service import AgentService
from app.api.health import http_client_dependency
from app.db.postgres import SessionLocal, engine, Base


logger = logging.getLogger("temp-agency")
router = APIRouter()


# Check if we need to create tables (for local development)
def setup_database():
    """Create database tables if running locally."""
    is_local = os.getenv("CLOUD_RUN", "False").lower() != "true"
    if is_local:
        logger.info(
            "Running in local environment, creating database tables if they don't exist"
        )
        Base.metadata.create_all(bind=engine)
    else:
        logger.info("Running in cloud environment, skipping table creation")


# Call the setup function when the module loads
setup_database()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_httpx_client() -> httpx.AsyncClient:
    """
    Dependency to provide HTTP client.

    Returns:
        An AsyncClient instance
    """
    if http_client_dependency.client is None:
        # This should ideally not happen if lifespan event works correctly
        raise HTTPException(status_code=503, detail="HTTP client not available.")
    return http_client_dependency.client


@router.post(
    "/register_agent/", response_model=AgentRegistrationResponse, status_code=200
)
async def register_agent(
    agent_service_url: str = Body(
        ...,
        embed=True,
        description="The base URL of the agent service whose card should be registered.",
    ),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client),
    db: Session = Depends(get_db),
):
    """
    Register an agent with the Temp Agency.

    Args:
        agent_service_url: The base URL of the agent service whose card should be registered
        httpx_client: HTTP client for making the request
        db: Database session

    Returns:
        A confirmation message indicating success or failure
    """
    if not agent_service_url.startswith("http://") and not agent_service_url.startswith(
        "https://"
    ):
        raise HTTPException(
            status_code=400,
            detail="Invalid agent_service_url provided. Must be http or https.",
        )

    try:
        agent_card_model = await AgentService.fetch_public_agent_card(
            agent_service_url, httpx_client
        )
    except Exception as e:
        logger.error(
            "Temp-Agency: Error fetching agent card from %s: %s",
            agent_service_url,
            e,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch agent card from {agent_service_url}: {str(e)}",
        ) from e

    if not agent_card_model:
        raise HTTPException(
            status_code=400,
            detail=f"Could not fetch or parse a valid public agent card from {agent_service_url}.",
        )

    # Use the URL from the fetched card if available and valid, otherwise the provided service URL
    db_key_url = (
        str(agent_card_model.url) if agent_card_model.url else agent_service_url
    )

    # Convert Pydantic model to dict for storage
    agent_data = agent_card_model.model_dump(exclude_none=True)
    agent_name = agent_card_model.name

    try:
        # Check if another agent already exists with the same name but different URL
        existing_agent = (
            db.query(Agent)
            .filter(Agent.name == agent_name, Agent.url != db_key_url)
            .first()
        )

        if existing_agent:
            raise HTTPException(
                status_code=409,
                detail=f"Another agent with name '{agent_name}' already exists with URL '{existing_agent.url}'. Name must be unique.",
            )

        # Check if agent with this URL already exists
        existing_agent = db.query(Agent).filter(Agent.url == db_key_url).first()

        if existing_agent:
            # Update existing agent
            existing_agent.name = agent_name
            existing_agent.data = agent_data
            existing_agent.updated_at = datetime.now()
            db.commit()
            message = f"Agent '{agent_name}' updated successfully using card from {db_key_url}."
        else:
            # Create new agent
            new_agent = Agent(
                url=db_key_url, name=agent_name, is_freelancer=True, data=agent_data
            )
            db.add(new_agent)
            db.commit()
            message = f"Agent '{agent_name}' registered successfully using card from {db_key_url}."

        return {
            "status": "success",
            "message": message,
        }
    except IntegrityError as e:
        db.rollback()
        logger.error(
            "Temp-Agency: Database integrity error during agent registration: %s",
            e,
            exc_info=True,
        )
        # Check if this is a duplicate key error for the name or URL constraint
        if "unique constraint" in str(e).lower() and "name" in str(e).lower():
            raise HTTPException(
                status_code=409,
                detail=f"Agent with name '{agent_name}' already exists. Names must be unique.",
            ) from e
        elif "unique constraint" in str(e).lower() and "url" in str(e).lower():
            raise HTTPException(
                status_code=409, detail=f"Agent with URL '{db_key_url}' already exists."
            ) from e
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register/update agent in database: {str(e)}",
        ) from e
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            "Temp-Agency: Database error during agent registration: %s",
            e,
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to register/update agent in database: {str(e)}",
        ) from e


@router.get("/agents/", response_model=AgentListResponse)
async def get_registered_agents(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(
        10, ge=1, le=100, description="Maximum number of items to return"
    ),
    db: Session = Depends(get_db),
):
    """
    Get a list of registered agents.

    Args:
        skip: Number of items to skip
        limit: Maximum number of items to return
        db: Database session

    Returns:
        A list of agents with pagination information
    """
    try:
        # Get total count
        total = db.query(Agent).count()

        # Get agents with pagination
        agents_query = db.query(Agent).offset(skip).limit(limit).all()

        # Convert SQLAlchemy objects to dictionaries
        agents = []
        for agent in agents_query:
            agent_dict = {
                "id": agent.id,
                "url": agent.url,
                "name": agent.name,
                "is_freelancer": agent.is_freelancer,
                **agent.data,  # Unpack the JSON data field
            }
            agents.append(agent_dict)

        return {
            "total": total,
            "skip": skip,
            "limit": limit,
            "agents": agents,
        }
    except Exception as e:
        logger.error(
            "Temp-Agency: Error fetching agents from database: %s", e, exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch agents from database: {str(e)}",
        ) from e


@router.get("/agents/by-name/{agent_name}")
async def get_agent_by_name(
    agent_name: str,
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client),
    db: Session = Depends(get_db),
):
    """
    Get agent details by name with health check.

    Args:
        agent_name: The name of the agent to retrieve
        httpx_client: HTTP client for making the request
        db: Database session

    Returns:
        The agent details with health information
    """
    try:
        # Using case-insensitive search for better user experience (if your DB supports it)
        # For PostgreSQL, we can use ilike for case-insensitive matching
        agent = db.query(Agent).filter(Agent.name.ilike(agent_name)).first()

        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with name '{agent_name}' not found.",
            )

        # Check agent health before returning
        health_info = await AgentService.check_agent_health(agent.url, httpx_client)

        # Convert SQLAlchemy object to dictionary
        agent_dict = {
            "id": agent.id,
            "url": agent.url,
            "name": agent.name,
            "is_freelancer": agent.is_freelancer,
            "health": health_info,
            **agent.data,  # Unpack the JSON data field
        }

        return agent_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Temp-Agency: Error fetching agent by name: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch agent from database: {str(e)}",
        ) from e


@router.get("/agents/by-url")
async def get_agent_by_url(
    url: str = Query(..., description="The agent URL to search for"),
    httpx_client: httpx.AsyncClient = Depends(get_httpx_client),
    db: Session = Depends(get_db),
):
    """
    Get agent details by URL with health check.

    Args:
        url: The URL of the agent to retrieve
        httpx_client: HTTP client for making the request
        db: Database session

    Returns:
        The agent details with health information
    """
    try:
        agent = db.query(Agent).filter(Agent.url == url).first()
        if not agent:
            raise HTTPException(
                status_code=404,
                detail=f"Agent with URL '{url}' not found.",
            )

        # Check agent health before returning
        health_info = await AgentService.check_agent_health(url, httpx_client)

        # Convert SQLAlchemy object to dictionary
        agent_dict = {
            "id": agent.id,
            "url": agent.url,
            "name": agent.name,
            "is_freelancer": agent.is_freelancer,
            "health": health_info,
            **agent.data,  # Unpack the JSON data field
        }

        return agent_dict
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Temp-Agency: Error fetching agent by URL: %s", e, exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch agent from database: {str(e)}",
        ) from e


@router.delete("/deregister_agent/by-url", response_model=AgentDeregistrationResponse)
async def deregister_agent_by_url(
    url: str = Query(..., description="The URL of the agent to deregister"),
    db: Session = Depends(get_db),
):
    """
    Deregister an agent by its URL.

    Args:
        url: The URL of the agent to deregister
        db: Database session

    Returns:
        A confirmation message indicating success or failure
    """
    try:
        agent = db.query(Agent).filter(Agent.url == url).first()
        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent with URL '{url}' not found."
            )

        # Delete agent
        db.delete(agent)
        db.commit()

        logger.info("Temp-Agency: Successfully deregistered agent with URL '%s'", url)
        return {
            "status": "success",
            "message": f"Agent with URL '{url}' successfully deregistered.",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            "Temp-Agency: Error deregistering agent by URL: %s", e, exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deregister agent: {str(e)}",
        ) from e


@router.delete(
    "/deregister_agent/by-name/{agent_name}", response_model=AgentDeregistrationResponse
)
async def deregister_agent_by_name(
    agent_name: str,
    db: Session = Depends(get_db),
):
    """
    Deregister an agent by its name.

    Args:
        agent_name: The name of the agent to deregister
        db: Database session

    Returns:
        A confirmation message indicating success or failure
    """
    try:
        # Using case-insensitive search if your database supports it
        agent = db.query(Agent).filter(Agent.name.ilike(agent_name)).first()
        if not agent:
            raise HTTPException(
                status_code=404, detail=f"Agent with name '{agent_name}' not found."
            )

        # Delete agent
        db.delete(agent)
        db.commit()

        logger.info(
            "Temp-Agency: Successfully deregistered agent with name '%s'", agent_name
        )
        return {
            "status": "success",
            "message": f"Agent with name '{agent_name}' successfully deregistered.",
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            "Temp-Agency: Error deregistering agent by name: %s", e, exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to deregister agent: {str(e)}",
        ) from e
