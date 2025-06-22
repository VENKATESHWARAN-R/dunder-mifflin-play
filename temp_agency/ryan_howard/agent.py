"""
This is the main Agent module for the Ryan Howard agent
when running 'adk web' from the parent directory of this file.
this module initializes the agent with its capabilities,
and provides methods for streaming responses and handling queries.
"""

import os
from typing import Any, AsyncIterable, Callable, List, Union

from google.adk.agents import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService, InMemorySessionService, Session
from google.genai import types
from ryan_howard.config import agent_config
from ryan_howard.tools.data_science_tools import DataScienceTools

# import mlflow


# from dunder_mifflin_shared.agents import BaseDMAgent

# mlflow.set_tracking_uri("http://127.0.0.1:5000")
# mlflow.set_experiment("my-tracing-experimen-adk")

# mlflow.gemini.autolog()


class BaseDMAgent:
    """
    BaseAgent encapsulates common functionality for LLM-based agents, including
    agent construction, streaming responses, and standardized attributes.
    """

    def __init__(
        self,
        model: str,
        user_id: str,
        name: str,
        description: Union[str, Callable],
        instruction: Union[str, Callable],
        tools: List[Any] = None,
        # user_input_tool: Callable = None,
    ):
        """
        Initialize BaseAgent with model parameters, description, instructions, and tools.

        Args:
            model (str): LLM model identifier.
            user_id (str): Unique user name.
            name (str): Name of the agent.
            description (str): Short agent description.
            instruction (str): System prompt/instructions for the LLM.
            tools (List[Any]): List of tool callables exposed to the agent.
            user_input_tool (Callable): Optional tool for requesting user input.
        """
        self._model = model
        self._user_id = user_id
        self._name = name
        self.agent_description = description
        self.agent_instruction = instruction

        # ---> Tool config for requesting user input
        # self._user_input_tool = user_input_tool or request_user_input
        # self._user_input_tool_name = self._user_input_tool.__name__
        # if tools:
        #     tools.append(self._user_input_tool)
        #     self._tools = list(set(tools))
        # else:
        #     self._tools = [self._user_input_tool]
        # <--- End of tool config

        self._agent = self._build_agent(tools)
        self._runner = Runner(
            app_name=self._agent.name,
            agent=self._agent,
            session_service=DatabaseSessionService(
                db_url=os.getenv("DATABASE_URL", "sqlite:///db.sqlite3")
            )
            if os.getenv("DATABASE_URL")
            # Use in-memory session service if no database URL is provided
            else InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
            artifact_service=InMemoryArtifactService(),
        )

    def get_processing_message(self) -> str:
        """
        Return a standardized message shown while processing a request.
        """
        return "Processing your request..."

    def _build_agent(self, tools: List[Any]) -> LlmAgent:
        """
        Construct the underlying LlmAgent with shared properties.

        Args:
            tools: callable tools to register with the agent.

        Returns:
            An initialized LlmAgent.
        """

        return LlmAgent(
            model=self._model
            if self._model.startswith("gemini")
            else LiteLlm(model=self._model),
            name=self._name,
            description=self.agent_description,
            instruction=self.agent_instruction,
            tools=tools,
        )

    async def _upsert_session(
        self, session_id: str, user_id: str, state: dict = None
    ) -> Session:
        """
        Upsert a session in the session service, creating it if it doesn't exist.
        Args:
            session_id (str): Identifier for the conversation session.
            user_id (str): Identifier for the user.
            state (dict, optional): Initial state for the session.
        Returns:
            Session: The session object, either newly created or fetched.
        """

        session = await self._runner.session_service.get_session(
            app_name=self._agent.name,
            user_id=user_id,
            session_id=session_id,
        )
        if session is None:
            session = await self._runner.session_service.create_session(
                app_name=self._agent.name,
                user_id=user_id,
                state=state or {},
                session_id=session_id,
            )
        return session

    def _extract_response_text(self, event, is_final_response: bool) -> Any:
        """
        Extract text or function response from event content.

        Args:
            event: The event from the runner.
            is_final_response: Whether this is a final response.

        Returns:
            Extracted text or function response, or None if not available.
        """
        if not event.content or not event.content.parts:
            return None

        parts = [p.text for p in event.content.parts if p.text]
        if parts:
            return "\n".join(parts)

        # Include function responses only if it's a final response
        if is_final_response:
            func_resp = next(
                (
                    p.function_response.model_dump()
                    for p in event.content.parts
                    if p.function_response
                ),
                None,
            )
            return func_resp

        return None

    def _extract_token_counts(self, event) -> dict[str, int]:
        """
        Extract token usage metadata from event.

        Args:
            event: The event from the runner.

        Returns:
            Dictionary containing available token counts.
        """
        token_counts = {}

        if not hasattr(event, "usage_metadata") or not event.usage_metadata:
            return token_counts

        if hasattr(event.usage_metadata, "candidate_token_count"):
            token_counts["candidate_token_count"] = (
                event.usage_metadata.candidate_token_count
            )

        if hasattr(event.usage_metadata, "prompt_token_count"):
            token_counts["prompt_token_count"] = event.usage_metadata.prompt_token_count

        if hasattr(event.usage_metadata, "total_token_count"):
            token_counts["token_count"] = event.usage_metadata.total_token_count

        return token_counts

    def _build_response_dict(
        self, is_final_response: bool, response: Any, token_counts: dict[str, int]
    ) -> dict[str, Any]:
        """
        Build the response dictionary based on event data.

        Args:
            is_final_response: Whether this is a final response.
            response: The extracted response text or function result.
            token_counts: Dictionary of token counts.

        Returns:
            Response dictionary to yield.
        """
        result = {
            "is_task_complete": is_final_response,
        }

        # Add content or updates based on availability
        if is_final_response:
            result["content"] = response
        else:
            result["updates"] = response if response else self.get_processing_message()

        # Add token counts if available
        if token_counts:
            result["token_counts"] = token_counts

        return result

    async def stream_response(
        self, query: str, session_id: str, user_id: str = ""
    ) -> AsyncIterable[dict[str, Any]]:
        """
        Stream the agent's response events, yielding interim updates and final results.

        Args:
            query (str): The user or agent query text.
            session_id (str): Identifier for the conversation session.
            user_id (str, optional): Override the default user_id if provided from request.

        Yields:
            dict: { 'is_task_complete': bool, 'updates' or 'content': str or dict }
        """
        # Use provided user_id if available, otherwise use the default
        effective_user_id = user_id if user_id and user_id.strip() else self._user_id

        # Ensure session exists or create it
        session = await self._upsert_session(
            session_id=session_id,
            user_id=effective_user_id,
            state={"user_id": effective_user_id},
        )

        content = types.Content(role="user", parts=[types.Part.from_text(text=query)])
        async for event in self._runner.run_async(
            user_id=effective_user_id, session_id=session.id, new_message=content
        ):
            is_final = event.is_final_response()

            # Extract response text or function response if available
            response = self._extract_response_text(event, is_final)

            # modyfy the response to end the flow if user_input is required
            # This will be useful for A2A standards
            # function_calls = event.get_function_calls() or []
            # if function_calls and any(
            #     call.name == self._user_input_tool_name for call in function_calls
            # ):
            #     for call in function_calls:
            #         if call.name == self._user_input_tool_name:
            #             is_final = True
            #             response = request_user_input(
            #                 "Please provide the required input."
            #             )

            # Extract token usage metadata
            token_counts = self._extract_token_counts(event)

            # Build and yield the response dictionary
            result = self._build_response_dict(is_final, response, token_counts)
            yield result

    async def handle_query(self, query: str, session_id: str) -> List[dict]:
        """
        Convenience wrapper to consume the stream and return all messages.
        """
        results = []
        async for msg in self.stream_response(query, session_id):
            results.append(msg)
        return results


class RyanHowardAgent(BaseDMAgent):
    """A Data science agent that can do various data analysis tasks."""

    SUPPORTED_CONTENT_TYPES: List[str] = ["text", "text/plain"]

    @classmethod
    def get_agent(cls) -> LlmAgent:
        """
        Get the agent instance for this class.
        This is useful for accessing the agent without instantiating it.
        """
        return cls()._agent

    def __init__(self):
        self._tools = DataScienceTools()
        super().__init__(
            model=agent_config.model_id,
            user_id=agent_config.user_id,
            name=agent_config.agent_name,
            description=agent_config.description,
            instruction=agent_config.instruction,
            tools=[
                self._tools.load_csv,
                self._tools.get_basic_info,
                self._tools.get_summary_statistics,
                self._tools.plot_histograms,
                self._tools.get_unique_values,
                self._tools.get_data_sample,
                self._tools.create_boxplot,
                self._tools.create_scatter_plot,
                self._tools.plot_correlation_heatmap,
                self._tools.plot_pie_chart,
                self._tools.modify_dataset,
                self._tools.encode_categorical_columns,
                self._tools.read_file_from_gcs,
                self._tools.upload_file_to_gcs,
            ],
        )


root_agent = RyanHowardAgent.get_agent()
