"""
Models package for Temp Agency service.
"""

from app.models.models import (
    AgentHealthInfo,
    AgentRegistrationRequest,
    AgentRegistrationResponse,
    AgentDeregistrationResponse,
    AgentListResponse,
    HealthCheckResponse
)

__all__ = [
    "AgentHealthInfo",
    "AgentRegistrationRequest",
    "AgentRegistrationResponse",
    "AgentDeregistrationResponse", 
    "AgentListResponse",
    "HealthCheckResponse"
]
