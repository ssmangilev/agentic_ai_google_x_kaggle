import os

from typing import AsyncGenerator
from typing_extensions import override

from google.adk.tools import AgentTool
from google.adk.agents import (
    BaseAgent,
    LlmAgent,
    LoopAgent,
    SequentialAgent,
)
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from langfuse import observe

from agents.analyst import analyst_agent
from agents.chart_generator import chart_generator_agent
from agents.report_generator import report_generator_agent
from agents.report_pre_generator import report_pre_generator_agent
from agents.sql_executor import sql_executor_agent
from agents.validator import validator_agent
from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage, langfuse


prompt = langfuse_prompt_storage.get_prompt(
    os.getenv('DECIDER_PROMPT_NAME'))


# decider_agent = create_agent(
#     opentelemetry_span_name="Agent.Build.Decider",
#     agent_name="decider_agent",
#     model_name="gemini-2.0-flash-exp",
#     prompt=prompt,
#     tools=[
#         AgentTool(analyst_agent),
#         AgentTool(chart_generator_agent),
#         AgentTool(report_generator_agent),
#         AgentTool(report_pre_generator_agent),
#         AgentTool(sql_executor_agent),
#         AgentTool(validator_agent)]
# )


# class DeciderAgent(BaseAgent):
#     analyst_agent: LlmAgent
#     chart_generator_agent: LlmAgent
#     report_generator_agent: LlmAgent
#     report_pre_generator_agent: LlmAgent
#     sql_executor_agent: LlmAgent
#     validator_agent: LlmAgent

#     loop_agent: LoopAgent
#     sequential_agent: SequentialAgent

#     model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

#     def __init__(self, name, analyst_agent,
#                  chart_generator_agent,
#                  report_generator_agent,
#                  report_pre_generator_agent,
#                  sql_executor_agent,
#                  validator_agent):
#         # Create internal agents *before* calling super().__init__
#         loop_agent = LoopAgent(
#             name="PreGeneratorValidatorLoop",
#             sub_agents=[report_pre_generator_agent, validator_agent],
#             max_iterations=2)
#         sequential_agent = SequentialAgent(
#             name="AnalystChartGenerator", sub_agents=[
#                 analyst_agent,
#                 chart_generator_agent]
#         )
#         sub_agents_list = [
#             sql_executor_agent,
#             report_generator_agent,
#             loop_agent,
#             sequential_agent,
#         ]
#         super().__init__(
#             name=name,
#             analyst_agent=analyst_agent,
#             chart_generator_agent=chart_generator_agent,
#             report_generator_agent=report_generator_agent,
#             report_pre_generator_agent=report_pre_generator_agent,
#             sql_executor_agent=sql_executor_agent,
#             validator_agent=validator_agent,
#             loop_agent=loop_agent,
#             sequential_agent=sequential_agent,
#             sub_agents_list=sub_agents_list
#         )

#     @override
#     @observe
#     async def _run_async_impl(
#         self, ctx: InvocationContext
#     ) -> AsyncGenerator[Event, None]:
#         """
#         Implements the custom orchestration logic for the story workflow.
#         Uses the instance attributes assigned by Pydantic (e.g., self.analyst_agent).
#         """
        
#         with langfuse.start_as_current_observation(as_type="span", name="process-request") as current_span:

#             current_span.update(
#                 output=f"[{self.name}] Starting BI Workflow"
#             )

#             current_span.update(
#                 output=f"[{self.name}] Checking attached files"
#             )
#             files = ctx.attachments  # Or ctx.files, ctx.file_references, etc.

#             file_reference = files[0] if files else None

#             if not file_reference:
#                 current_span.update(
#                     output=f"[{self.name}] Files were not found"
#                 )

#                 # 1. Try to select data from a table
#                 current_span.update(
#                     output=f"[{self.name}] Running SQL Executor..."
#                 )
#                 async for event in self.sql_executor_agent.run_async(ctx):
#                     current_span.update(
#                         output=f"[{self.name}] Event from SQL Executor: {event.model_dump_json(indent=2, exclude_none=True)}") # NOQA
#                     if event.is_final_response():
#                         payload = event.payload if hasattr(event, 'payload') else event.output # NOQA

#                         if isinstance(payload, dict) and 'data' in payload:
#                             sql_output_data = payload.get('data')
#                             current_span.update(
#                                 output=f"[{self.name}] Final SQL Output Captured. Data rows: {len(sql_output_data) if sql_output_data else 0}") # NOQA

#                     # Yield the event to the calling function (your orchestrator loop)
#                     yield event

#                 # 2. Check if data was selected after the SQL Executor is complete
#                 if sql_output_data is None or len(sql_output_data) == 0:
#                     current_span.update(
#                         output=f"[{self.name}] SQL Executor returned NO DATA. Terminating BI flow."
#                     )
#                     # You would yield an error event or trigger a failure agent here
#                     # yield ErrorEvent(message="No data selected from table.")
#                     return  # Stop the orchestration flow

#                 # 3. If data exists, proceed to the next step (e.g., Data Analyser)
#                 current_span.update(
#                     output=f"[{self.name}] Data selected successfully. Proceeding to Data Analyser."
#                 )

#                 async for event in self.sequential_agent.run_async(ctx):
#                     current_span.update(
#                         output=f"{self.name} Analysis started."
#                     )
#                     yield event

#                 current_span.update(
#                     output=f"[{self.name}] Analysis finished successfully. Proceeding to post-analysis validation."
#                 )

#                 async for event in self.loop_agent.run_async(ctx):
#                     current_span.update(
#                         output=f"{self.name} Validation started."
#                     )
#                     yield event

#                 current_span.update(
#                     output=f"[{self.name}] Validation finished successfully. Proceeding to report generation."
#                 )

#                 async for event in self.report_generator_agent.run_async(ctx):
#                     current_span.update(
#                         output=f"{self.name} Report generation started."
#                     )
#                     yield event

#                 current_span.update(
#                     output=f"[{self.name}] Workflow finished."
#                 )


# decider_agent = DeciderAgent(
#     name="DeciderAgent",
#     analyst_agent=analyst_agent,
#     chart_generator_agent=chart_generator_agent,
#     report_generator_agent=report_generator_agent,
#     report_pre_generator_agent=report_pre_generator_agent,
#     sql_executor_agent=sql_executor_agent,
#     validator_agent=validator_agent
# )