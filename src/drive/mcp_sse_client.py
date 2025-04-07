import asyncio

from pydantic_ai import Agent
from pydantic_ai.mcp import MCPServerHTTP
from pydantic_ai.models.gemini import GeminiModel

from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

server = MCPServerHTTP(url='http://localhost:3001/sse')
gemini_model = GeminiModel('gemini-2.0-pro-exp-02-05', provider="google-gla")

agent = Agent(
    gemini_model,
    tools=[duckduckgo_search_tool()],
)

async def main():
    async with agent.run_mcp_servers():
        pass

if __name__ == "__main__":
    asyncio.run(main())
