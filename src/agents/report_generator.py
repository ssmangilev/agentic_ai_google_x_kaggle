import os

from google.adk.tools import function_tool, load_memory

from tools.render_pdf import render_final_pdf
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage
from utils.sanitaze import sanitize_agent_tools


prompt = langfuse_prompt_storage.get_prompt(
    os.getenv('REPORT_GENERATOR_PROMPT_NAME'))


report_generator_agent = create_agent(
    opentelemetry_span_name="Agent.Build.Report",
    agent_name="report_generator_agent",
    model_name="gemini-2.5-flash",
    prompt=prompt,
    tools=[
        function_tool.FunctionTool(render_final_pdf),
        load_memory]
)

sanitize_agent_tools(report_generator_agent)
