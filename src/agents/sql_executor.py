import os

from google.adk.tools import code_execution, load_memory
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
# from mcp import StdioServerParameters

from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage


prompt = langfuse_prompt_storage.get_prompt(os.getenv('EXECUTOR_PROMPT_NAME'))


sql_executor_agent = create_agent(
    opentelemetry_span_name="Agent.Build.SQL",
    agent_name="sql_executor_agent",
    model="gemini-2.5-flash",
    prompt=prompt,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                command="npx",
                args=[
                    "-y",
                    "@modelcontextprotocol/server-postgres",
                    f"{os.getenv("POSTGRES_DATABASE")}"])),
        load_memory,
        code_execution]
)
