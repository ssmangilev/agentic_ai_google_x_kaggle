import os

from google.adk.tools import load_memory
from google.adk.tools.function_tool import FunctionTool

from tools.save_chart_image import save_chart_image
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage
from utils.sanitaze import sanitize_agent_tools


prompt = langfuse_prompt_storage.get_prompt(
    os.getenv('CHART_GENERATOR_PROMPT_NAME'))


chart_generator_agent = create_agent(
    opentelemetry_span_name="Agent.Build.Chart",
    agent_name="chart_generator_agent",
    model_name="gemini-2.5-flash",
    prompt=prompt,
    tools=[
        FunctionTool(save_chart_image),
        load_memory]
)


sanitize_agent_tools(chart_generator_agent)
