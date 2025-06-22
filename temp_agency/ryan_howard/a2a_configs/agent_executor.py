"""
This module defines the RyanHowardAgentExecutor class, which is responsible for executing
the Ryan Howard agent's tasks. It inherits from BaseAgentExecutor to reuse common functionality.
"""

import logging
from abc import ABC, abstractmethod
from collections import Counter
from typing import Any, Dict, Type

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import Part, TaskState, TextPart, UnsupportedOperationError
from a2a.utils import new_agent_text_message, new_task
from a2a.utils.errors import ServerError

# from dunder_mifflin_shared.utils import (  # GenAIClient,; get_state_sys_instruction,
#     BoolChoice, prepare_prompt)
from ryan_howard.agent import RyanHowardAgent

# from dunder_mifflin_shared.agent_executor import BaseAgentExecutor


# from google.genai.types import GenerateContentConfig


logger = logging.getLogger(__name__)


class BaseAgentExecutor(AgentExecutor, ABC):
    """Base class for all agent executors in the Dunder Mifflin system."""

    def __init__(self, agent: Any = None, genai_model: str = None):
        """
        Initialize the executor with an agent instance.

        Args:
            agent: The agent instance that will handle the actual processing.
                  If None, the subclass should set self.agent in its own __init__.
            genai_model: Optional; the model to use for GenAI interactions.
                If not provided, it defaults to the environment variable GENAI_MODEL or "gemini-2.0-flash-lite".
        """
        if agent is not None:
            self.agent = agent
        # self.genai_model = genai_model
        # self.genai_client = GenAIClient(genai_model) if genai_model else None
        # self.genai_config = GenerateContentConfig(
        #     system_instruction=get_state_sys_instruction(),
        #     response_mime_type="text/x.enum",
        #     response_schema=BoolChoice,
        # )

    @abstractmethod
    def _get_agent_class(self) -> Type[Any]:
        """
        Abstract method to get the agent class.
        Must be implemented by subclasses.

        Returns:
            Type[Any]: The agent class (not instance) for this executor.
        """
        pass

    def _extract_user_id(self, context: RequestContext) -> str:
        """
        Extract user_id from the message metadata if available.

        Args:
            context: The request context containing the message.

        Returns:
            str: The extracted user ID or an empty string if not found.
        """
        user_id = ""
        if hasattr(context, "message") and context.message:
            message_data = getattr(context.message, "dict", lambda: {})()
            if isinstance(message_data, dict) and "metadata" in message_data:
                metadata = message_data["metadata"]
                if isinstance(metadata, dict) and "user_id" in metadata:
                    user_id = metadata["user_id"]
        return user_id

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """
        Execute the agent task with the given context and event queue.

        Args:
            context: The request context containing the message and task information.
            event_queue: The event queue for sending messages back to the client.
        """
        # Extract user ID and query
        token_counts: Dict[str, int] = Counter()  # for token usage tracking
        require_user_input = False
        user_id = self._extract_user_id(context)
        query = context.get_user_input()

        # Get or create a task
        task = context.current_task
        if not task:
            if context.message is None:
                raise ValueError("context.message is None, cannot create a new task.")
            task = new_task(context.message)
            await event_queue.enqueue_event(task)

        # Create task updater
        updater = TaskUpdater(event_queue, task.id, task.contextId)

        # Stream response from the agent
        async for item in self.agent.stream_response(query, task.contextId, user_id):
            is_task_complete = (
                item["is_task_complete"] if "is_task_complete" in item else False
            )
            # Update token counts if available
            token_counts += (
                item["token_counts"] if "token_counts" in item else Counter()
            )

            # if is_task_complete and self.genai_model:
            #     logger.info(
            #         "Classifying state of the agent for task %s with model %s",
            #         task.id,
            #         self.genai_model,
            #     )
            #     output_classifier_prompt = prepare_prompt(
            #         user_input=query,
            #         model_output=item["content"] if "content" in item else "",
            #     )
            #     # Use GenAI client to classify the state of the agent
            #     genai_response = await self.genai_client.invoke(
            #         output_classifier_prompt,
            #         config=self.genai_config,
            #     )
            #     require_user_input = genai_response == BoolChoice.TRUE.value
            #     logger.info(
            #         "State classification result for task %s: %s (requires user input: %s)",
            #         task.id,
            #         genai_response,
            #         str(require_user_input),
            #     )

            # Extract the message content to avoid nested conditional expressions
            if "updates" in item:
                message_content = item["updates"]
            elif "content" in item:
                message_content = item["content"]
            else:
                message_content = ""
            # if task is not completed and user input is not required,
            # we can update the task status with the agent's updates
            if not is_task_complete and not require_user_input:
                await updater.update_status(
                    TaskState.working,
                    new_agent_text_message(
                        message_content,
                        task.contextId,
                        task.id,
                    ),
                )
            # If User input is required, we need to handle it
            elif require_user_input:
                await updater.update_status(
                    TaskState.input_required,
                    new_agent_text_message(message_content, task.contextId, task.id),
                    final=True,  # Indicate that this chunk is final from the agent
                )
                break  # Exit the loop to wait for user input
            else:
                # If the task is complete, we can finalize the task
                await updater.add_artifact(
                    [Part(root=TextPart(text=message_content))],
                    name="response",
                    metadata=dict(token_counts),  # Include token counts in metadata
                )
                await updater.complete()
                break

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:
        """
        Cancel the current task. By default, this operation is not supported.
        Subclasses can override this method to implement cancellation.

        Args:
            context: The request context.
            event_queue: The event queue.

        Raises:
            ServerError: With UnsupportedOperationError if not implemented.
        """
        raise ServerError(error=UnsupportedOperationError())


class RyanHowardAgentExecutor(BaseAgentExecutor):
    """Ryan Howard agent executor that inherits from the base executor."""

    def __init__(self, genai_model: str = None):
        """Initialize the executor with a Ryan Howard agent instance."""
        # Create the agent first
        agent = RyanHowardAgent()
        # Pass the agent to the parent class __init__
        super().__init__(agent=agent)

    def _get_agent_class(self) -> Type[Any]:
        """Get the agent class for this executor."""
        return RyanHowardAgent
