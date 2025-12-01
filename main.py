import chainlit as cl
import uuid
import sys
import os

# Add the 'src' directory to the Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from dotenv import load_dotenv

from google.genai import types

from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.agents import SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

from agents.security_guard import security_guard_agent
from agents.decider import decider_agent


from utils.memory_service import memory_service


load_dotenv()


# Setup Database Session Service
db_url = "sqlite+aiosqlite:///my_agent_data.db"  # Local SQLite file
session_service = DatabaseSessionService(db_url=db_url)


main_pipeline = SequentialAgent(
    name="main_pipeline",
    sub_agents=[security_guard_agent, decider_agent]
)

app = App(
    name="bi_agentic_system",
    root_agent=main_pipeline,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,
        overlap_size=1,
    ),
)


# Initialize the Runner
runner = Runner(
    app=app,
    session_service=session_service,
    memory_service=memory_service
)


@cl.on_message
async def main(message: cl.Message):
    """
    Main Chainlit message handler.
    1. Sets up the session ID.
    2. Runs the agent system (runner.run_async).
    3. Streams the output back to the user via Chainlit's streaming mechanism.
    """
    # 1. Generate a unique session ID for this conversation thread
    session_id = f"cl_{uuid.uuid4().hex[:8]}"

    # 2. Create the session in the session service
    await session_service.create_session(
        app_name="bi_agentic_system",
        user_id=cl.user_session.get("id", "anonymous_user"),
        session_id=session_id
    )

    # 3. Prepare the input message for the runner
    # IMPORTANT: Use message.content to get the text input
    query_content = types.Content(
        role="user",
        parts=[types.Part(text=message.content)]
    )

    # 4. Initialize Chainlit streaming message
    # This will be the message box the user sees filling up in real-time
    msg = cl.Message(content="")

    # 5. Run the agent asynchronously and stream the output
    async for event in runner.run_async(
        user_id=cl.user_session.get("id", "anonymous_user"),
        session_id=session_id,
        new_message=query_content
    ):
        # The runner yields events; we only care about events with text parts
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    # Stream the text chunk to the Chainlit frontend
                    await msg.stream_token(part.text)

    # 6. Once the stream is complete, update the message with any
    # final details (optional)
    await msg.send()
