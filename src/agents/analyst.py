import os

from google.adk.tools import load_memory
from google.adk.tools.function_tool import FunctionTool

from tools import load_dataset
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage
from utils.sanitaze import sanitize_agent_tools


prompt = langfuse_prompt_storage.get_prompt(os.getenv('ANALYST_PROMPT_NAME'))


analyst_agent = create_agent(
    opentelemetry_span_name="Agent.Build.Analyst",
    agent_name="analyst_agent",
    model_name="gemini-2.5-flash",
    prompt=prompt,
    tools=[load_memory, FunctionTool(load_dataset)]
)

sanitize_agent_tools(analyst_agent)
