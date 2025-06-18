import os
from typing import List, Tuple
import vertexai
from vertexai import agent_engines
from vertexai.preview import reasoning_engines
from google.adk.sessions.session import Session
from vertexai.agent_engines._agent_engines import AgentEngine
from dotenv import load_dotenv
from scranton.agents.michael_scott.agent import root_agent as michael_scott_agent

load_dotenv()


def main():
    print("Starting the Michael Scott agent deployment...")

    # Initialize the Vertex AI SDK
    vertexai.init(
        project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION"),
        staging_bucket=os.getenv("GOOGLE_CLOUD_STAGING_BUCKET"),
    )

    print("Vertex AI initialized with project:", os.getenv("GOOGLE_CLOUD_PROJECT"))

    # app = reasoning_engines.AdkApp(
    #     agent=michael_scott_agent,
    #     enable_tracing=True,
    # )

    # session: Session = app.create_session(user_id="venkat", state={"role": "Client"})
    # print("Session created with ID:", session.id)

    # # another session for the same user
    # session: Session = app.create_session(user_id="venkat", state={"role": "Client"})
    # print("Another session created with ID:", session.id)

    # all_sessions: List[Tuple[str, List[Session]]] = app.list_sessions(user_id="venkat")

    # print("All sessions for user 'venkat':")
    # for s in all_sessions:
    #     _, sessions = s
    #     for ses in sessions:
    #         print(f"Session ID: {ses.id}, State: {ses.state}")

    # for event in app.stream_query(
    #     user_id="venkat",
    #     session_id=session.id,
    #     message="i want to talk to prison mike",
    # ):
    #     print(event)

    # print("Creating the Michael Scott agent engine...")

    # remote_app = agent_engines.create(
    #     agent_engine=michael_scott_agent,
    #     requirements=["google-cloud-aiplatform[adk,agent_engines]", "python-dotenv>=1.1.0"],
    # )

    # print("Michael Scott agent engine created successfully.")
    # print(remote_app.resource_name)

    print("inferencing with the Michael Scott agent engine...")
    agent_engine: AgentEngine = agent_engines.get(
        resource_name="7102634009200427008",
    )

    #remote_session = agent_engine.create_session(user_id="venkat")
    # remote_session = agent_engine.get_session(user_id="venkat", session_id="8499572878138671104")
    # print(remote_session)

    # for event in agent_engine.stream_query(
    #     user_id="venkat",
    #     session_id=remote_session["id"],
    #     message="who are you and what do you do?",
    # ):
    #     print(event)

    agent_engine.delete(force=True)

    # remote_app = agent_engines.create(
    #         agent_engine=michael_scott_agent,
    #         requirements=[
    #             "google-cloud-aiplatform[adk,agent_engines]",
    #             "python-dotenv>=1.1.0",

    #         ],
    #         extra_packages=["./adk_short_bot"],
    #     )


if __name__ == "__main__":
    main()
