import os
import json
import asyncio

import typer

from mcp import ClientSession, StdioServerParameters
from mcp.types import CallToolResult
from mcp.client.stdio import stdio_client


async def client():
    server_params = StdioServerParameters(
        command="uv",
        args=["run", "mcp_server.py", "server"],
        env=os.environ
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            web_result: CallToolResult = await session.call_tool(
                "groq_web_search", {"query": "Who wrote the office US?"}
            )

            save_file = await session.call_tool(
                "save_file", {"file_name": "office", "file_content": "HAHAHHHAAHHARERESTSTSJFIFJSOFJIOSD", "extension": ".txt"}
            )
            read_file = await session.call_tool(
                "read_file", {"file_name": "office.txt"}
            )

            print(read_file)


if __name__ == "__main__":
    asyncio.run(client())
