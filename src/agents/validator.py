import os

from tools.validate_report import validate_report_draft
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage

prompt = langfuse_prompt_storage.get_prompt(os.getenv('VALIDATOR_PROMPT_NAME'))


validator_agent = create_agent(
    opentelemetry_span_name="Agent.Build.Validation",
    agent_name="validator_agent",
    model_name="gemini-2.5-flash",
    prompt=prompt,
    tools=[
        validate_report_draft,],
    output_key='validation'
)
