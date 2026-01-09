import sys
from engineio.payload import Payload

# Increase the packet limit (default is usually 16, which is too low for some apps)
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
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService

from agents.security_guard import security_guard_agent
from agents.sql_executor import sql_executor_agent
# from agents.decider import decider_agent
from agents.analyst import analyst_agent
from agents.validator import validator_agent
from agents.report_generator import report_generator_agent

from tools.save_pdf import create_pdf_file_tool
from tools.upload_file_to_the_cloud import upload_local_file_to_cloud
from utils.memory_service import memory_service

from langfuse import observe, propagate_attributes

import re


load_dotenv()


# Setup Database Session Service
db_url = "sqlite+aiosqlite:///my_agent_data.db"  # Local SQLite file
session_service = DatabaseSessionService(db_url=db_url)

artifact_service = InMemoryArtifactService()

save_pdf_from_content_agent = Agent(
    name="save_pdf_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a technical automation agent. Your ONLY job is to save content to PDF files.
    
    CRITICAL RULES:
    1. Do NOT chat. Do NOT say "Okay" or "I will do that".
    2. If you receive text content and a request to save it, IMMEDIATELY call the `create_pdf_file_tool`.
    3. Use the entire preceding analysis text as the `text_content` argument.
    4. Never output plain text to the user. Only use the tool.
    """,
    tools=[create_pdf_file_tool],
    output_key="pdf",
)

main_pipeline = SequentialAgent(
    name="main_pipeline",
    sub_agents=[analyst_agent, validator_agent, save_pdf_from_content_agent]
)

app = App(
    name="agents",
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
    memory_service=memory_service,
    artifact_service=artifact_service
)


@cl.on_message
@observe
async def main(message: cl.Message):
    session_id = f"cl_{uuid.uuid4().hex[:8]}"
    user_id = cl.user_session.get("id", "anonymous_user")

    with propagate_attributes(session_id=session_id):
        session = await session_service.create_session(
            app_name="agents",
            user_id=user_id,
            session_id=session_id
        )

        query_content = types.Content(
            role="user",
            parts=[types.Part(text=message.content)]
        )

        # Initialize the message
        msg = cl.Message(content="")
        input_data = {"table_name": message.content, "timestamp": str(datetime.now())}

        # Track the full response text to scan for images later
        full_response_text = ""
        elements = []
        processed_files = set() # Prevent duplicate renders

        async for event in runner.run_async(
            user_id=cl.user_session.get("id", "anonymous_user"),
            session_id=session_id,
            new_message=query_content,
            state_delta=input_data,
        ):
            print(f"DEBUG: Event Author: {event.author}")
            if event.content and event.content.parts and event.content.parts[0].text:
                print(f"DEBUG [{event.author}]: {event.content.parts[0].text[:100]}...")
            if event.author == 'save_pdf_agent' and event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        full_response_text += part.text
                        await msg.stream_token(part.text)

                    if part.function_response:
                        # The tool has now finished 'save_artifact'
                        # Now it is safe to load it!
                        
                        # Use the filename the tool actually saved
                        filename = "wine_quality_analysis.pdf"
                        breakpoint()
                        artifact = await artifact_service.load_artifact(
                            app_name='agents',
                            user_id=user_id,
                            session_id=session_id,
                            filename=filename
                        )

                        if artifact:
                            file_content = artifact.inline_data.data if hasattr(artifact, 'inline_data') else artifact
                            elements.append(cl.File(
                                name=filename,
                                content=file_content,
                                display="inline"
                            ))
                            msg.elements = elements
                            await msg.update()

                        # matches = re.findall(r"Saved as artifact:\s*([\w\d_-]+\.png)", part.text)

                        # for filename in matches:
                        #         try:
                        #             # 1. Fetch the artifact
                        #             artifact = await artifact_service.load_artifact(
                        #                 app_name='agents',
                        #                 user_id=user_id,
                        #                 session_id=session_id,
                        #                 filename="filename")

                        #             # 2. Extract bytes (Google ADK stores them in .data)
                        #             if hasattr(artifact, 'inline_data'):
                        #                 image_content = artifact.inline_data.data
                        #             else:
                        #                 image_content = artifact
                        #             # 3. Create Chainlit element
                        #             elements.append(cl.Image(
                        #                 name=filename,
                        #                 content=image_content,
                        #                 display="inline"
                        #             ))

                        #             # 4. Update the UI immediately
                        #             msg.elements = elements
                        #             await msg.update()
                        #             processed_files.add(filename)

                        #         except Exception as e:
                        #             print(f"Error loading {filename}: {e}")

                    # Handle code display if desired
                    elif hasattr(part, 'executable_code') and part.executable_code:
                        await msg.stream_token(f"\n\n```python\n{part.executable_code.code}\n```\n")
    await msg.send()