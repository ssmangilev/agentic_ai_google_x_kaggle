import os

from typing import AsyncGenerator
from typing_extensions import override

from google.adk.agents import (
    BaseAgent,
    LlmAgent,
    SequentialAgent,
)
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event

from agents.analyst import analyst_agent
from agents.report_generator import report_generator_agent
from agents.sql_executor import sql_executor_agent
from agents.validator import validator_agent
from utils.prompt_storage import langfuse_prompt_storage, langfuse


prompt = langfuse_prompt_storage.get_prompt(
    os.getenv('DECIDER_PROMPT_NAME'))


class DeciderAgent(BaseAgent):
    analyst_agent: LlmAgent
    report_generator_agent: LlmAgent
    sql_executor_agent: LlmAgent
    validator_agent: LlmAgent

    model_config = {"arbitrary_types_allowed": True, "extra": "allow"}

    def __init__(self, name, analyst_agent,
                 report_generator_agent,
                 sql_executor_agent,
                 validator_agent):
        # Create internal agents *before* calling super().__init__

        super().__init__(
            name=name,
            analyst_agent=analyst_agent,
            report_generator_agent=report_generator_agent,
            sql_executor_agent=sql_executor_agent,
            validator_agent=validator_agent,
        )

    def _get_csv_pipeline(self):
        return SequentialAgent(
            name="CsvAnalystPipeline",
            sub_agents=[self.analyst_agent,
                        self.validator_agent,
                        self.report_generator_agent]
        )

    def _get_sql_pipeline(self):
        return SequentialAgent(
            name="SQLAnalystPipeline",
            sub_agents=[self.sql_executor_agent,
                        self.analyst_agent,
                        self.validator_agent,
                        self.report_generator_agent]
        )

    @override
    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        """
        Implements the custom orchestration logic for the story workflow.
        Uses the instance attributes assigned by Pydantic
        (e.g., self.analyst_agent).
        """

        with langfuse.start_as_current_observation(
                as_type="span", name="process-request"
        ):

            if ctx.session.state.get('csv', False):
                pipeline = self._get_csv_pipeline()
            else:
                pipeline = self._get_sql_pipeline()

            async for event in pipeline.run_async(ctx):
                yield event


decider_agent = DeciderAgent(
    name="DeciderAgent",
    analyst_agent=analyst_agent,
    report_generator_agent=report_generator_agent,
    sql_executor_agent=sql_executor_agent,
    validator_agent=validator_agent
)
