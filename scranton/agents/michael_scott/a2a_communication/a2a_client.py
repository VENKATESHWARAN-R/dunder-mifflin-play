import os
import json
import uuid
import base64
import httpx
from typing import Any, Dict, List

from a2a.client import A2AClient, A2ACardResolver
from a2a.types import (
    AgentCard,
    MessageSendParams,
    SendMessageRequest,
    SendMessageResponse,
    SendMessageSuccessResponse,
    Task,
)
from google.adk.tools.tool_context import ToolContext


async def fetch_agent_card(
    agent_url: str,
    # username: str = USERNAME,
    # password: str = PASSWORD,
) -> str:
    """
    Fetches the AgentCard from agent_url and returns it as a dict.

    Args:
        agent_url (str): The URL of the agent to fetch the card from.
    """
    async with httpx.AsyncClient(timeout=30) as client:
        resolver = A2ACardResolver(client, agent_url)
        card: AgentCard = await resolver.get_agent_card()
        # Convert to simple dict; you can also use card.model_dump_json()
        agent_info = json.dumps({"name": card.name, "description": card.description})
        return agent_info


async def send_message_to_agent(
    agent_url: str,
    message: str,
    tool_context: ToolContext,
    # username: str = USERNAME,
    # password: str = PASSWORD,
) -> str:
    """
    Sends message as a user to the agent at agent_url.

    Args:
        agent_url (str): The URL of the agent to send the message to.
        message (str): The message to send to the agent.
        tool_context (ToolContext): The context for the tool, which includes state management.

    Returns:
        str: The response message from the agent.
    """

    user_id: str = "Michael_Scott"
    # Add trailing slash if not present
    if not agent_url.endswith("/"):
        agent_url += "/"
    # Step 1: fetch the card
    async with httpx.AsyncClient(timeout=30) as client:
        # resolver = A2ACardResolver(client, agent_url)
        # card: AgentCard = await resolver.get_agent_card()

        # Step 2: set up A2A client with Basic auth
        # credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
        # auth_headers = {"Authorization": f"Basic {credentials}"}
        agent_client = A2AClient(client, url=agent_url)

        # Step 3: build unique IDs
        state = tool_context.state
        task_id = state.get("task_id", str(uuid.uuid4()))
        context_id = state.get("context_id", str(uuid.uuid4()))
        message_id = str(uuid.uuid4())

        # Step 4: prepare payload
        payload = {
            "message": {
                "role": "user",
                "parts": [{"type": "text", "text": message}],
                "messageId": message_id,
                "taskId": task_id,
                "contextId": context_id,
                "metadata": {"user_id": user_id},
            }
        }
        params = MessageSendParams.model_validate(payload)
        request = SendMessageRequest(id=message_id, params=params)

        # Step 5: send and parse
        response: SendMessageResponse = await agent_client.send_message(
            request,  # http_kwargs={"headers": auth_headers}
        )

    # Step 6: extract reply parts
    if not isinstance(response.root, SendMessageSuccessResponse) or not isinstance(
        response.root.result, Task
    ):
        raise RuntimeError("Unexpected response type from agent")

    if (
        not hasattr(tool_context.state, "context_id")
        or not tool_context.state["context_id"]
    ):
        tool_context.state["context_id"] = (
            response.root.result.context_id
            if hasattr(response.root.result, "context_id")
            else context_id
        )
    result_json = json.loads(response.root.model_dump_json(exclude_none=True))
    parts: List[str] = []
    final_message = "No response received from remote agent."
    for artifact in result_json.get("result", {}).get("artifacts", []):
        for part in artifact.get("parts", []):
            if isinstance(part, dict) and "text" in part:
                # Ensure part is a dict with 'text' key
                parts.append(part["text"])

    final_message = "\n".join(parts) if parts else final_message
    print(f"Final message from remote agent: {final_message}")
    return final_message
