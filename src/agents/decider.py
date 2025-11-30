import os

from google.adk.tools import AgentTool

from agents.analyst import analyst_agent
from agents.chart_generator import chart_generator_agent
from agents.report_generator import report_generator_agent
from agents.report_pre_generator import report_pre_generator_agent
from agents.sql_executor import sql_executor_agent
from agents.validator import validator_agent
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage


prompt = langfuse_prompt_storage.get_prompt(
    os.getenv('DECIDER_PROMPT_NAME'))


decider_agent = create_agent(
    opentelemetry_span_name="Agent.Build.Decider",
    agent_name="decider_agent",
    model="gemini-2.5-flash",
    prompt=prompt,
    sub_agents=[
        AgentTool(analyst_agent),
        AgentTool(chart_generator_agent),
        AgentTool(report_generator_agent),
        AgentTool(report_pre_generator_agent),
        AgentTool(sql_executor_agent),
        AgentTool(validator_agent)]
)
