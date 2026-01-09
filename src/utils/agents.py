import json

from google.adk.agents import Agent
from google.adk.tools import load_memory

from google.adk.code_executors.built_in_code_executor import BuiltInCodeExecutor

from opentelemetry import trace

from typing import Callable

from langfuse import observe


tracer = trace.get_tracer(__name__)


def extract_tool_info(tool):
    """Helper to extract serializable info from opaque Tool objects"""
    try:
        # Check standard attributes usually found on Tool/Agent objects
        if hasattr(tool, 'name'):
            return tool.name
        if hasattr(tool, '__name__'):
            return tool.__name__
        # If AgentTool wraps an agent, it might store it in .agent
        if hasattr(tool, 'agent') and hasattr(tool.agent, 'name'):
            return f"AgentTool({tool.agent.name})"
        return str(tool)
    except Exception:
        return "Unknown Tool"


@observe
def create_agent(
    opentelemetry_span_name: str,
    agent_name: str,
    model_name: str,
    prompt: str,
    output_key: str,
    tools: list[Callable] | None = None,
    save_context_callback: Callable | None = None,
    code_executor: BuiltInCodeExecutor | None = None,
) -> Agent:
    """Factory function to create the configured agent."""

    _tools = [load_memory]
    if tools:
        _tools.extend(tools)

    # ---------------------------------------------------------
    # FIX: Manually extract tool names for the trace
    # ---------------------------------------------------------
    # We create a list of strings (names) which JSON can easily handle
    tool_names = [extract_tool_info(t) for t in _tools]

    # Get the current span created by @observe or tracer
    current_span = trace.get_current_span()

    # Manually set the attribute. This will override or add to the
    # default empty object inputs in many UI views, or appear as a tag.
    current_span.set_attribute("agent.tool_names", json.dumps(tool_names))

    with tracer.start_as_current_span(opentelemetry_span_name):
        if code_executor is not None:
            return Agent(
                name=agent_name,
                model=model_name,
                instruction=prompt,
                code_executor=code_executor,
                after_agent_callback=save_context_callback,
                output_key=output_key,
            )
        return Agent(
            name=agent_name,
            model=model_name,
            instruction=prompt,
            tools=_tools,
            after_agent_callback=save_context_callback,
            output_key=output_key,
        )
