import asyncio
from dataclasses import dataclass

import logfire
from devtools import debug
from httpx import AsyncClient
from pydantic_ai import Agent
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider
from pydantic_ai.tools import RunContext

# from models.task import Task
# from schemas.task import TaskIn, TaskOut
logfire.configure()


# TODO ADD AUTH, maybe jwt, cookie, w/e

Agent.instrument_all()

BASE_URL = "http://localhost:8000"
TASKS_URL = BASE_URL + "/api/v1/tasks"


@dataclass
class TaskAgentDeps:
    http_client: AsyncClient


groq_model = GroqModel("qwen-2.5-coder-32b")
gemini_model = GeminiModel(
    model_name="gemini-2.0-pro-exp-02-05",
)
ollama_model = OpenAIModel(model_name="phi4:latest", provider=OpenAIProvider(base_url="http://localhost:11434/v1"))
ollama_coder_agent = Agent(
    ollama_model,
    system_prompt="You are a python expert, you write clean and maintainable code.",
    retries=5,
    model_settings={
        "max_tokens": 2048,
        "temperature": 0.2,
    },
)


task_agent = Agent(
    groq_model,
    system_prompt=("Use the `get_task` tool to get the task content."),
    deps_type=TaskAgentDeps,
    retries=2,
    instrument=True,
)


@task_agent.tool
async def get_task(ctx: RunContext[TaskAgentDeps], task_id: int):
    response = await ctx.deps.http_client.get(f"{TASKS_URL}/", params={"task_id": task_id})
    response.raise_for_status()
    return response.text


async def main():
    async with AsyncClient() as client:
        deps = TaskAgentDeps(http_client=client)
        result = await task_agent.run("Get the task with ID: `1`", deps=deps)
        debug(result)
        print("Response:", result.data)


if __name__ == "__main__":
    asyncio.run(main())
