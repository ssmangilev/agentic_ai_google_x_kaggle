from google.adk.agents import Agent
from google.adk.code_executors import BuiltInCodeExecutor

from opentelemetry import trace

from typing import Callable


tracer = trace.get_tracer(__name__)


def create_agent(
    opentelemetry_span_name: str,
    agent_name: str,
    model_name: str,
    prompt: str,
    tools: list[Callable] | None,
    save_context_callback: Callable | None = None,
    agent_type: Agent.__class__ = Agent,
) -> Agent:
    """Factory function to create the configured agent."""

    with tracer.start_as_current_span(opentelemetry_span_name):
        return Agent(
            name=agent_name,
            model=model_name,
            instruction=prompt,
            tools=tools,
            after_agent_callback=save_context_callback,
            code_executor=BuiltInCodeExecutor()
        )
