import sys
from engineio.payload import Payload

# Increase the packet limit (default is usually 16,
# which is too low for some apps)
Payload.max_decode_packets = 500

import chainlit as cl
import uuid
import sys
import os

from datetime import datetime

# Add the 'src' directory to the Python path
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from dotenv import load_dotenv

from google.genai import types

from google.adk.apps.app import App, EventsCompactionConfig
from google.adk.agents import Agent, SequentialAgent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.adk.artifacts.in_memory_artifact_service import (
    InMemoryArtifactService,
)

from agents.security_guard import security_guard_agent
from agents.sql_executor import sql_executor_agent
from agents.decider import decider_agent
from agents.analyst import analyst_agent
from agents.validator import validator_agent
from agents.report_generator import report_generator_agent

from tools.save_pdf import create_pdf_file_tool
from utils.memory_service import memory_service
from utils.prompt_storage import langfuse

from langfuse import observe, propagate_attributes

import re


load_dotenv()


# Setup Database Session Service
db_url = "sqlite+aiosqlite:///my_agent_data.db"  # Local SQLite file
session_service = DatabaseSessionService(db_url=db_url)

artifact_service = InMemoryArtifactService()

main_pipeline = SequentialAgent(
    name="main_pipeline",
    sub_agents=[decider_agent]
)

app = App(
    name="agents",
    root_agent=decider_agent,
    events_compaction_config=EventsCompactionConfig(
        compaction_interval=3,
        overlap_size=1,
    ),
)


# Initialize the Runner
runner = Runner(
    app=app,
    session_service=session_service,
    memory_service=memory_service,
    artifact_service=artifact_service
)


@cl.on_message
@observe
async def main(message: cl.Message):
    session_id = f"cl_{uuid.uuid4().hex[:8]}"
    user_id = cl.user_session.get("id", "anonymous_user")

    with propagate_attributes(session_id=session_id):
        await session_service.create_session(
            app_name="agents",
            user_id=user_id,
            session_id=session_id
        )

        query_content = types.Content(
            role="user",
            parts=[types.Part(text=message.content)]
        )
        csv_content = None
        if message.elements and message.elements[0]:
            file = message.elements[0]
            name = file.name
            if name.endswith('.csv'):
                with open(file.path, "r") as f:
                    csv_content = f.read()

        # Initialize the message
        msg = cl.Message(content="")
        input_data = {
            "table_name": message.content,
            "timestamp": str(datetime.now())}

        if csv_content:
            query_content = types.Content(
                role="user",
                parts=[
                    types.Part(text=csv_content)])
            input_data['csv'] = True

        # Track the full response text to scan for images later
        full_response_text = ""
        elements = []

        async for event in runner.run_async(
            user_id=cl.user_session.get("id", "anonymous_user"),
            session_id=session_id,
            new_message=query_content,
            state_delta=input_data,
        ):
            print(f"DEBUG: Event Author: {event.author}")
            if event.content and event.content.parts and event.content.parts[0].text: # NOQA
                print(f"DEBUG [{event.author}]: {event.content.parts[0].text[:100]}...") # NOQA
            if event.author == 'report_generator_agent' and event.content and event.content.parts: # NOQA
                for part in event.content.parts:
                    if part.text:
                        full_response_text += part.text
                        await msg.stream_token(part.text)

                    if part.function_response:
                        # The tool has now finished 'save_artifact'
                        # Now it is safe to load it!

                        # Use the filename the tool actually saved
                        filename = "report.pdf"
                        artifact = await artifact_service.load_artifact(
                            app_name='agents',
                            user_id=user_id,
                            session_id=session_id,
                            filename=filename
                        )

                        if artifact:
                            file_content = artifact.inline_data.data \
                                if hasattr(artifact, 'inline_data') \
                                else artifact
                            elements.append(cl.File(
                                name=filename,
                                content=file_content,
                                display="inline"
                            ))
                            msg.elements = elements
                            await msg.update()
            if event.author == 'analyst_agent' and event.content and event.content.parts: # NOQA
                for part in event.content.parts:
                    # Handle code display if desired
                    if hasattr(part, 'executable_code') and part.executable_code: # NOQA
                        langfuse.update_current_span(metadata={"generated_code": part.executable_code.code}) # NOQA
    await msg.send()
