"""
This module will be used to deploy the agents on the vertex AI platform.
"""

import os
import json
from pathlib import Path
import sys
import importlib
import argparse
from typing import Optional, Any, Dict

import vertexai
from vertexai import agent_engines
from dotenv import load_dotenv

from scripts.agent_models import AgentsConfig, AgentConfig
from scripts.agent_config import AGENTS_CONFIG

from scranton.agents.holly_flax.agent import root_agent as holly_flax_agent

# Load environment variables
load_dotenv()

GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT")
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
GCP_STAGING_BUCKET = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET")

# Constants
this_file = Path(__file__).resolve()
scripts_dir = this_file.parent
REQUIREMENTS_BASE_PATH = scripts_dir.parent


def get_agent_config(agent_name: str) -> AgentsConfig:
    """Retruns the agent configuration object for the given agent name.
    If the agent name is not found, it raises a ValueError.
    
    Args:
        agent_name (str): The name of the agent to load.
    Returns:
        AgentsConfig: The configuration object for the agent.
    Raises:
        ValueError: If the agent name is not found in the configuration.
    """
    agents = AGENTS_CONFIG.get("agents", {})
    if agent_name not in agents:
        raise ValueError(f"Agent '{agent_name}' not found in configuration.")
    agent_config = agents[agent_name]
    return AgentsConfig(agents={agent_name: AgentConfig(**agent_config)})

def initialize_vertex_ai() -> None:
    """Initialize the Vertex AI SDK using environment variables."""
    
    if not all([GCP_PROJECT, GCP_LOCATION, GCP_STAGING_BUCKET]):
        raise ValueError("Missing required environment variables. Please set GOOGLE_CLOUD_PROJECT, GOOGLE_CLOUD_LOCATION, and GOOGLE_CLOUD_STAGING_BUCKET")
    
    vertexai.init(
        project=GCP_PROJECT,
        location=GCP_LOCATION,
        staging_bucket=GCP_STAGING_BUCKET,
    )
    
    print(f"Vertex AI initialized with project: {GCP_PROJECT}")


# def import_agent(agent_config: AgentConfig) -> Any:
#     """Import an agent using its module path from the configuration.
    
#     Args:
#         agent_config (AgentConfig): The configuration object for the agent.
    
#     Returns:
#         Any: The imported agent module.
    
#     Raises:
#         ImportError: If the module cannot be imported.
#     """
#     module_path = agent_config.module_path
#     try:
#         module = importlib.import_module(module_path)
#         return module.root_agent
#     except ImportError as e:
#         print(f"Error importing module '{module_path}': {e}")
#         sys.exit(1)


def deploy_agent(agent_name: str) -> str:
    """Deploy an agent and return its resource name.
    
    Args:
        agent_name (str): The name of the agent to deploy.
    
    Returns:
        str: The resource name of the deployed agent.
    
    Raises:
        ValueError: If the agent name is not found in the configuration.
    """
    agent_config = get_agent_config(agent_name)
    if not agent_config:
        print(f"Error: Unknown agent '{agent_name}'.")
        sys.exit(1)
    
    print(f"Starting the {agent_config.agents[agent_name].display_name} agent deployment...")
    
    # Import the agent
    agent = agent_config.agents[agent_name].agent
    requirements = agent_config.agents[agent_name].requirements
    if isinstance(requirements, str):
        requirements_path = REQUIREMENTS_BASE_PATH / requirements.strip("./").replace("/", os.sep)
        requirements_data = str(requirements_path)
    elif isinstance(requirements, list):
        requirements_data = requirements
    else:
        requirements_data = None
    
    # Update the Vertex AI configuration with the agent-specific bucket
    vertexai.init(
        project=GCP_PROJECT,
        location=GCP_LOCATION,
        staging_bucket=GCP_STAGING_BUCKET,
    )
    
    # Deploy the agent
    try:
        response = agent_engines.create(
            agent_engine=holly_flax_agent,
            display_name=agent_config.agents[agent_name].display_name,
            description=agent_config.agents[agent_name].description,
            requirements=requirements_data,
            env_vars=agent_config.agents[agent_name].env_vars,
        )
        print(f"Agent '{agent_name}' deployed successfully.")
        return response.resource_name
    except Exception as e:
        print(f"Error deploying agent '{agent_name}': {e}")
        sys.exit(1)

def test_agent(resource_name: str, test_message: str = "Who are you and what do you do?") -> None:
    """Test an agent by creating a session and sending a test message."""
    print(f"Testing agent with resource name: {resource_name}")
    
    # Get the deployed agent
    agent_engine = agent_engines.get(resource_name=resource_name)
    
    # Create a new session and test the agent
    print("Creating a new session...")
    try:
        # Try to access create_session method using getattr to avoid static type checking errors
        # The actual object at runtime should have these methods
        create_session_method = getattr(agent_engine, "create_session", None)
        stream_query_method = getattr(agent_engine, "stream_query", None)
        
        if create_session_method is not None and stream_query_method is not None:
            # Use dynamic method access
            session = create_session_method(user_id="test_user")
            session_id = session["id"]
            print(f"Session created with ID: {session_id}")
            
            # Send a test message
            print(f"Sending test message: '{test_message}'")
            print("Agent response:")
            
            for event in stream_query_method(
                user_id="test_user",
                session_id=session_id,
                message=test_message
            ):
                print(event)
        else:
            print("Could not find appropriate methods in the agent_engine object.")
            print("Available methods and attributes:")
            for attr in dir(agent_engine):
                if not attr.startswith('_'):  # Skip private/internal attributes
                    print(f"  - {attr}")
    except Exception as e:
        print(f"Error testing agent: {e}")
        print("The API may have changed. Please check the Vertex AI documentation for the latest API.")


def delete_agent(resource_name: str) -> None:
    """Delete an agent."""
    print(f"Deleting agent with resource name: {resource_name}")
    
    agent_engine = agent_engines.get(resource_name=resource_name)
    agent_engine.delete(force=True)
    
    print("Agent deleted successfully")



def list_agents() -> None:
    """List all available agents."""
    agents = AGENTS_CONFIG.get("agents", {})
    if not agents:
        print("No agents found in the configuration.")
        return
    
    print("Available agents:")
    for agent_name, agent_config in agents.items():
        print(f"- {agent_name}: {agent_config['display_name']}")



def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Deploy and test agents")
    
    parser.add_argument("action", choices=["deploy", "test", "delete", "list"], 
                        help="Action to perform: deploy, test, delete, or list agents")
    
    parser.add_argument("--agent", type=str,
                        help="Name of the agent to deploy, test, or delete")
    
    parser.add_argument("--resource-name", type=str,
                        help="Resource name of the deployed agent (required for test/delete)")
    
    parser.add_argument("--test-message", type=str, default="Who are you and what do you do?",
                        help="Message to send when testing the agent")
    
    return parser.parse_args()



def main():
    args = parse_args()

    if args.action == "list":
        list_agents()
        return
    
    initialize_vertex_ai()

    if args.action == "deploy":
        if not args.agent:
            print("Error: Agent name is required for deployment")
            sys.exit(1)
        
        resource_name = deploy_agent(args.agent)
        print(f"To test this agent, run: python {sys.argv[0]} test --resource-name {resource_name}")
        print(f"To delete this agent, run: python {sys.argv[0]} delete --resource-name {resource_name}")
    
    elif args.action == "test":
        if not args.resource_name:
            print("Error: Resource name is required for testing")
            sys.exit(1)
        
        test_agent(args.resource_name, args.test_message)
    
    elif args.action == "delete":
        if not args.resource_name:
            print("Error: Resource name is required for deletion")
            sys.exit(1)
        
        delete_agent(args.resource_name)

if __name__ == "__main__":
    main()
# This script is designed to deploy, test, and manage agents on the Vertex AI platform.
# It allows you to deploy agents defined in a configuration file, test them by sending messages, and delete them when no longer needed.
