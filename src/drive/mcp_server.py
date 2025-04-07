import logfire
import pathlib
import shutil

from typing import List, Optional, Dict

from dataclasses import dataclass
from contextlib import asynccontextmanager

from mcp.server.fastmcp import FastMCP
from sqlalchemy.ext.asyncio.session import AsyncSession
from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.groq import GroqModel

from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.common_tools.duckduckgo import duckduckgo_search_tool

import httpx

from models import WebsearchResult


logfire.configure()
Agent.instrument_all()

BASE_DIR = pathlib.Path.cwd() / "data"
BASE_DIR.mkdir(exist_ok=True)
BASE_URL = "http://localhost:8000"

server = FastMCP("pydanticAI server")

ollama_model = OpenAIModel(model_name="gemma3:12b", provider=OpenAIProvider(base_url="http://localhost:11434/v1"))
gemini_model = GeminiModel('gemini-2.0-pro-exp-02-05', provider="google-gla")
groq_model = GroqModel("meta-llama/llama-4-scout-17b-16e-instruct")

http_client = httpx.AsyncClient()


@dataclass
class AgentDeps:
    http_client: httpx.AsyncClient
    db_session: AsyncSession


agent = Agent(
    gemini_model,
    tools=[duckduckgo_search_tool()],
    system_prompt="Search the DuckDuckGo search tool with provided query. Show sources.",
)

ollama_agent = Agent(
    ollama_model,
    tools=[duckduckgo_search_tool()],
    system_prompt="You are a helpful assistant, help with the task at hand.",
    retries=5,
    model_settings={
        "max_tokens": 1024,
        "temperature": 0.5,
    }
)

groq_search_agent = Agent(
    groq_model,
    tools=[duckduckgo_search_tool()],
    system_prompt="Search the DuckDuckGo search tool with provided query. Show sources.",
    model_settings={
        "max_tokens": 512,
        "temperature": 0.2
    }
)

groq_code_agent = Agent(
    groq_model,
    system_prompt="",
    deps_type=AgentDeps
)


@server.tool()
async def sanitize_input(input: str):
    pass


@server.tool()
async def get_task_content(task_id: int):
    response = await http_client.get("http://localhost:8000/tasks/")
    response.raise_for_status()

    print(response.text)
    # return f"Task: {response.text}"


@server.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get personlized greetings"""
    return f"Hello, {name}!"


@server.prompt()
def review_code(code: str) -> str:
    return f"Please review this code: \n\n{code}"


@server.tool()
async def save_file(file_name: str, file_content: str, extension: str) -> str:
    """Save file to specified dir"""
    (BASE_DIR / "coding").mkdir(exist_ok=True)
    file_path = BASE_DIR / "coding" / f"{file_name}{extension}"

    with open(file_path, "w") as f:
        f.write(file_content)

    return f"File saved at {file_path}"


@server.tool()
async def read_file(file_name: str) -> Dict[str, str]:
    """Read file from specified dir"""
    read_file = BASE_DIR / "coding" / file_name
    read_content = read_file.read_text(encoding="utf-8")
    return {
        "file_name": file_name,
        "content": read_content
    }


@server.tool()
async def summarize_file(content: str) -> Dict[str, str]:
    """Summarize the file contents"""
    summarized = await groq_code_agent.run(f"Summarize file content: {content}")

# @server.tool()
# async def prepare_web_search(content: str) -> str:
#     """Generate search queries based on file content"""
#     queries = await groq_search_agent.run(
#         f"Generate "
#     )

@server.tool()
async def web_search(query: str) -> str:
    r = await agent.run(
        f"Search DuckDuckGo for the given query: {query}",
        result_type=WebsearchResult
    )
    return r.data.result


@server.tool()
async def ollama_web_search(query: str) -> str:
    r = await ollama_agent.run(
        f"Search DuckDuckGo for the given query: {query}",
        result_type=WebsearchResult
    )
    return r.data.result


@server.tool()
async def groq_web_search(query: str):
    r = await groq_search_agent.run(
        f"Search DuckDuckGo for the given query: {query}",
        result_type=WebsearchResult
    )
    return r.all_messages()


@server.tool()
async def ask(query: str) -> str:
    r = await agent.run(f"{query}")
    return r.data


if __name__ == "__main__":
    server.run()
