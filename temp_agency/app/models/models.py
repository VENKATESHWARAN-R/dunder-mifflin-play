"""
Data models for the Temp Agency service.
"""

from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field, HttpUrl

from sqlalchemy import Column, Integer, String, Boolean, JSON, TIMESTAMP, text
from app.db.postgres import Base


class AgentHealthInfo(BaseModel):
    """Agent health status information."""

    is_online: bool = False
    last_checked: Optional[str] = None  # ISO format timestamp
    response_time_ms: Optional[float] = None


class AgentRegistrationRequest(BaseModel):
    """Request model for agent registration."""

    agent_service_url: HttpUrl = Field(
        ...,
        description="The base URL of the agent service whose card should be registered",
    )


class AgentRegistrationResponse(BaseModel):
    """Response model for agent registration."""

    status: str
    message: str


class AgentDeregistrationResponse(BaseModel):
    """Response model for agent deregistration."""

    status: str
    message: str


class AgentListResponse(BaseModel):
    """Response model for listing agents."""

    total: int
    skip: int
    limit: int
    agents: List[Dict[str, Any]]


class HealthCheckResponse(BaseModel):
    """Response model for service health check."""

    status: str = "healthy"
    postgres_connected: bool
    http_client_available: bool
    details: Optional[str] = None


class Agent(Base):
    __tablename__ = "agents_registry"
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    name = Column(String, unique=True, nullable=False)
    is_freelancer = Column(Boolean, nullable=False, default=True)
    data = Column(JSON, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
    updated_at = Column(TIMESTAMP(timezone=True), server_default=text("NOW()"))
