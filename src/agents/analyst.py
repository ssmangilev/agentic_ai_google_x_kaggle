import os

from google.adk.tools import code_execution, load_memory
from google.adk.tools.function_tool import FunctionTool

from tools import load_dataset
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage


prompt = langfuse_prompt_storage.get_prompt(os.getenv('ANALYST_PROMPT_NAME'))


analyst_agent = create_agent(
    opentelemetry_span_name="Agent.Build.Analyst",
    agent_name="analyst_agent",
    model="gemini-2.5-flash",
    prompt=prompt,
    tools=[code_execution, load_memory, FunctionTool(load_dataset)]
)
