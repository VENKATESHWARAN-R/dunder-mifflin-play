"""
This module defines the settings and configurations for the Ryan Howard agent.
"""

import os
from dataclasses import dataclass, field
from typing import Dict, Set
from dotenv import load_dotenv
from ryan_howard.prompts import get_agent_instruction, get_agent_description

# Load environment variables from .env file
load_dotenv()


@dataclass
class BaseAgentConfig:
    """Base configuration for agents in the Dunder Mifflin project."""

    # Server configuration
    host: str = field(default_factory=lambda: os.getenv("AGENT_HOST", "localhost"))
    port: str = field(default_factory=lambda: os.getenv("AGENT_PORT", "10010"))

    # API configuration
    temp_agency_url: str = field(
        default_factory=lambda: os.getenv("TEMP_AGENCY_URL", "http://localhost:8000")
    )

    # Agent identity - these can be overridden by subclasses
    user_id: str = field(
        default_factory=lambda: os.getenv("USER_ID", "Default")
    )  # Should be overridden during runtime
    model_id: str | None = field(default_factory=lambda: os.getenv("MODEL_ID", None))
    agent_id: str | None = field(default_factory=lambda: os.getenv("AGENT_ID", None))
    agent_name: str | None = field(
        default_factory=lambda: os.getenv("AGENT_NAME", None)
    )
    database_url: str | None = field(
        default_factory=lambda: os.getenv("DATABASE_URL", None)
    )

    # Security configurations
    api_keys: Dict[str, str] = field(default_factory=dict)
    users: Dict[str, str] = field(default_factory=dict)
    user_scopes: Dict[str, str] = field(
        default_factory=dict
    )  # User authorization scopes ('read', 'read_write', 'readonly')
    public_paths: Set[str] = field(default_factory=set)
    secure_agent: bool = field(
        default_factory=lambda: os.getenv("SECURE_AGENT", "false").lower() == "true"
    )

    # keeping the default to False since the authentication will be handled
    # if either api_keys or users or this secure_agent are set

    def __post_init__(self):
        """Set derived properties after initialization."""
        # Set URL using host and port
        self.url = os.getenv("AGENT_URL") or f"http://{self.host}:{self.port}"

        # Load users from environment variables
        self._load_users()

        # Load user scopes from environment variables
        self._load_user_scopes()

    def _load_users(self):
        """
        Load users and passwords from environment variables. This supports both individual
        user definitions and a bulk users string that can be split into multiple entries.

        Bulk format: "username1:password1,username2:password2,..."
        Individual format: AGENT_USERS

        Since agents run in isolated containers, we use generic environment variable names.
        """
        # Load bulk users from AGENT_USERS environment variable
        bulk_users = os.getenv("AGENT_USERS")
        if bulk_users:
            try:
                # Format: "username1:password1,username2:password2,..."
                for entry in bulk_users.split(","):
                    if ":" in entry:
                        username, password = entry.strip().split(":", 1)
                        if username and password:
                            self.users[username] = password
            except ValueError as e:
                print(f"Error parsing agent users: {e}")

    def _load_user_scopes(self):
        """
        Load user scopes from environment variables. This defines the authorization level
        for each user.

        Bulk format: "username1:read,username2:read_write,..."
        Valid scopes: 'read', 'read_write', 'readonly'

        Default scope is 'read' if not specified.

        Since agents run in isolated containers, we use generic environment variable names.
        """
        # Load bulk user scopes from AGENT_USER_SCOPES environment variable
        bulk_scopes = os.getenv("AGENT_USER_SCOPES")
        if not bulk_scopes:
            return

        try:
            self._process_user_scopes(bulk_scopes)
        except ValueError as e:
            print(f"Error parsing agent user scopes: {e}")

    def _process_user_scopes(self, bulk_scopes_str):
        """
        Helper method to process user scopes from a string.

        Args:
            bulk_scopes_str: A string containing user scopes in format "username1:read,username2:read_write,..."
        """
        valid_scopes = ["read", "read_write", "readonly"]

        for entry in bulk_scopes_str.split(","):
            if ":" not in entry:
                continue

            username, scope = entry.strip().split(":", 1)
            if not username or not scope:
                continue

            # Validate and store scope
            scope = scope.lower()
            if scope in valid_scopes:
                self.user_scopes[username] = scope
            else:
                print(
                    f"Invalid scope '{scope}' for user '{username}'. Using 'read' as default."
                )
                self.user_scopes[username] = "read"

    def check_authorization(self, username: str, action: str) -> bool:
        """
        Check if a user is authorized to perform a specific action based on their scope.

        Args:
            username: The username to check
            action: The action to verify ('read' or 'write')

        Returns:
            True if the user is authorized, False otherwise
        """
        if not username or username not in self.user_scopes:
            # Default to read-only access if user has no defined scope
            scope = "readonly"
        else:
            scope = self.user_scopes[username]

        if action.lower() == "read":
            # All scope levels can read
            return True
        elif action.lower() == "write":
            # Only read_write scope can write
            return scope.lower() == "read_write"

        # Default deny for unknown actions
        return False

@dataclass
class AgentConfig(BaseAgentConfig):
    """Configuration for the Ryan Howard agent."""

    # Override agent identity defaults for Ryan Howard
    user_id: str = field(
        default_factory=lambda: os.getenv("USER_ID", "Venkat")
    )  # Should be overridden during runtime
    model_id: str = field(
        default_factory=lambda: os.getenv("MODEL_ID", "gemini-2.0-flash-001")
    )
    agent_id: str = field(default_factory=lambda: os.getenv("AGENT_ID", "ryan_howard"))
    agent_name: str = field(
        default_factory=lambda: os.getenv("AGENT_NAME", "ryan_howard")
    )
    public_paths: set = field(
        default_factory=lambda: set(
            os.getenv("PUBLIC_PATHS", "/.well-known/agent.json").split(",")
        )
    )
    genai_model: str | None = field(
        default_factory=lambda: os.getenv("GENAI_MODEL", None)
    )

    @property
    def description(self) -> str:
        """Get the current agent description based on environment variables."""
        version = os.getenv("AGENT_DESCRIPTION_VERSION")
        return get_agent_description(version)

    @property
    def instruction(self) -> str:
        """Get the current agent instruction based on environment variables."""
        version = os.getenv("AGENT_INSTRUCTION_VERSION")
        return get_agent_instruction(version)

    # Note: We're now using the base class implementation of _load_users and _load_user_scopes
    # No need to override these methods since we're using generic environment variable names


# Instantiate the configuration
agent_config = AgentConfig()
