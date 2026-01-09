import os

from tools.save_pdf import create_pdf_file_tool
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage


prompt = langfuse_prompt_storage.get_prompt(
    os.getenv('REPORT_GENERATOR_PROMPT_NAME'))


report_generator_agent = create_agent(
    opentelemetry_span_name="Agent.Build.Report",
    agent_name="report_generator_agent",
    model_name="gemini-2.5-flash",
    prompt=prompt,
    tools=[
        create_pdf_file_tool],
    output_key='pdf'
)
