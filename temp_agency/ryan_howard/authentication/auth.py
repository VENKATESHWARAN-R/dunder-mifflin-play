"""
This module defines the authentication middleware for the Ryan Howard agent.
"""

import base64
import logging
import secrets
from typing import Optional, Dict, Set, ClassVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from ryan_howard.config import agent_config
# from dunder_mifflin_shared.auth import AuthMiddleware


logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Reusable middleware to handle authentication for all requests.

    This class can be inherited by specific agents to customize authentication.
    Override api_keys and users class variables, or implement custom verify methods.
    """

    # Class variables for authentication - should be overridden by subclasses
    api_keys: ClassVar[Dict[str, str]] = {}
    users: ClassVar[Dict[str, str]] = {}
    public_paths: ClassVar[Set[str]] = {"/.well-known/agent.json"}

    @classmethod
    def verify_api_key(cls, api_key: str) -> bool:
        """Verify if the API key is valid.

        Override this method in subclasses for custom API key verification.
        """
        if not cls.api_keys:
            logger.warning("No API keys configured. All API key checks will fail.")
        return api_key in cls.api_keys.values()

    @classmethod
    def get_user_from_api_key(cls, api_key: str) -> Optional[str]:
        """Get username from API key.

        Override this method in subclasses for custom user lookup.
        """
        if not cls.api_keys:
            logger.warning("No API keys configured. Cannot resolve user from API key.")
            return None
        for username, key in cls.api_keys.items():
            if key == api_key:
                return username
        return None

    @classmethod
    def verify_basic_auth(cls, username: str, password: str) -> bool:
        """Verify basic auth credentials.

        Override this method in subclasses for custom password verification.
        """
        if not cls.users:
            logger.warning("No users configured. All basic auth checks will fail.")
        stored_password = cls.users.get(username)
        if stored_password is None:
            return False
        return bool(secrets.compare_digest(stored_password, password))

    async def dispatch(self, request: Request, call_next):
        logger.info(f"Processing request: {request.method} {request.url.path}")
        # Skip auth for public endpoints
        if request.url.path in self.public_paths:
            return await call_next(request)

        # Helper function to handle authentication
        def authenticate_request(auth_header):
            if not auth_header:
                return JSONResponse(
                    status_code=401, content={"detail": "Authentication required"}
                )

            if auth_header.startswith("Bearer "):
                token = auth_header.replace("Bearer ", "")
                if not self.verify_api_key(token):
                    return JSONResponse(
                        status_code=401, content={"detail": "Invalid API key"}
                    )
                # Store the username in request state for later use
                request.state.user = self.get_user_from_api_key(token)

            elif auth_header.startswith("Basic "):
                credentials = base64.b64decode(
                    auth_header.replace("Basic ", "")
                ).decode("utf-8")
                username, password = credentials.split(":")
                if not self.verify_basic_auth(username, password):
                    return JSONResponse(
                        status_code=401, content={"detail": "Invalid credentials"}
                    )
                # Store the username in request state for later use
                request.state.user = username

            else:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Unsupported authentication method"},
                )
            return None

        auth_header = request.headers.get("Authorization")
        auth_response = authenticate_request(auth_header)
        if auth_response:
            return auth_response

        # Continue with the request
        return await call_next(request)


class RyanHowardAuthMiddleware(AuthMiddleware):
    """Authentication middleware for the Ryan Howard agent."""

    # Override class variables with Ryan Howard specific settings
    api_keys = agent_config.api_keys
    users = agent_config.users
    public_paths = agent_config.public_paths
