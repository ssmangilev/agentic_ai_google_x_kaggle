import os
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters

from utils.agents import create_agent
from utils.prompt_storage import langfuse_prompt_storage


prompt = langfuse_prompt_storage.get_prompt(os.getenv('EXECUTOR_PROMPT_NAME'))

database_url = os.getenv("POSTGRES_DATABASE")
workspace_folder = os.getenv("WORKSPACE_FOLDER", "/tmp")

print(prompt)


postgres_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-postgres",
                f"{database_url}"]),
        timeout=60,
    ),
)


filesystem_mcp = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command="npx",
            args=[
                "-y",
                "@modelcontextprotocol/server-filesystem",
                f"{workspace_folder}"]),
        timeout=60,
    ),
)


sql_executor_agent = create_agent(
    opentelemetry_span_name="Agent.Build.SQL",
    agent_name="sql_executor_agent",
    model_name="gemini-2.5-flash",
    prompt=prompt,
    tools=[postgres_mcp, filesystem_mcp],
    output_key='sql_data'
)
