"""
This module is for defining the agent models for the Vertex AI deployment scripts.
"""

from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel

from google.adk.agents import BaseAgent


class AgentConfig(BaseModel):
    """Configuration for a single agent."""

    agent: BaseAgent
    display_name: str
    description: Optional[str] = None
    gcs_dir_name: str
    requirements: Union[
        List[str], str
    ]  # Can be a list of requirements or a single string
    env_vars: Dict[str, Any]


class AgentsConfig(BaseModel):
    """Configuration for all agents."""

    agents: Dict[str, AgentConfig]

    def get_agent(self, agent_name: str) -> Optional[AgentConfig]:
        """Get configuration for a specific agent by name."""
        return self.agents.get(agent_name)
