import os

from google.adk.tools import load_memory
from google.adk.tools.function_tool import FunctionTool

from tools.check_content import process_content
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage


prompt = langfuse_prompt_storage.get_prompt(
    os.getenv('SECURITY_GUARD_PROMPT_NAME'))


security_guard_agent = create_agent(
    opentelemetry_span_name="Agent.Build.Security",
    agent_name="security_guard_agent",
    model="gemini-2.5-flash",
    prompt=prompt,
    tools=[
        FunctionTool(process_content),
        load_memory,]
)
