import os

from google.adk.tools import load_memory

from google.adk.code_executors.built_in_code_executor import BuiltInCodeExecutor

from tools.load_dataset import load_dataset
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage


prompt = langfuse_prompt_storage.get_prompt(os.getenv('ANALYST_PROMPT_NAME'))


analyst_agent = create_agent(
    opentelemetry_span_name="Agent.Build.Analyst",
    agent_name="analyst_agent",
    model_name="gemini-2.5-flash",
    prompt=prompt,
    code_executor=BuiltInCodeExecutor(),
    output_key='analysis'
)
