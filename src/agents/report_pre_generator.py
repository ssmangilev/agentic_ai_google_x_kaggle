import os

from google.adk.tools import load_memory
from google.adk.tools.function_tool import FunctionTool

from tools.render_pdf import render_final_pdf
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage
from utils.sanitaze import sanitize_agent_tools


prompt = langfuse_prompt_storage.get_prompt(
    os.getenv('REPORT_PREGENERATOR_PROMPT_NAME'))


report_pre_generator_agent = create_agent(
    opentelemetry_span_name="Agent.Build.PreReport",
    agent_name="report_pregenerator_agent",
    model_name="gemini-2.5-flash",
    prompt=prompt,
    tools=[
        FunctionTool(render_final_pdf),
        load_memory,]
)


sanitize_agent_tools(report_pre_generator_agent)
