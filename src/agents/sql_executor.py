import os

from google.adk.tools import load_memory
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage
from utils.sanitaze import sanitize_agent_tools


prompt = langfuse_prompt_storage.get_prompt(os.getenv('EXECUTOR_PROMPT_NAME'))

database_url = os.getenv("POSTGRES_DATABASE")

sql_executor_agent = create_agent(
    opentelemetry_span_name="Agent.Build.SQL",
    agent_name="sql_executor_agent",
    model_name="gemini-2.5-flash",
    prompt=prompt,
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params=StdioServerParameters(
                    command="npx",
                    args=[
                        "-y",
                        "@modelcontextprotocol/server-postgres",
                        f"{database_url}"]),
                timeout=60,
            ),
        ),
        load_memory]
)

sanitize_agent_tools(sql_executor_agent)
