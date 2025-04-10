import sys
import pathlib
import asyncio

from typing import List, Dict, Union
from httpx import Response

from pydantic import BaseModel, Field

from pydantic_ai import Agent
from pydantic_ai.models.groq import GroqModel
from pydantic_ai.models.gemini import GeminiModel
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

ROOT_DIR = pathlib.Path(__file__).parent.resolve()
BASE_DIR = pathlib.Path(ROOT_DIR / "data")
CODING_DIR = BASE_DIR / "coding"
CODING_DIR.mkdir(exist_ok=True)

groq_model = GroqModel("qwen-2.5-coder-32b")
gemini_model = GeminiModel(
    model_name="gemini-2.0-pro-exp-02-05",
)
ollama_model = OpenAIModel(
    model_name="granite3.2:latest", provider=OpenAIProvider(base_url="http://localhost:11434/v1")
)


class Task(BaseModel):
    id: int = Field()
    name: str = Field()
    description: str = Field()
    example: str = Field()


class TaskResult(BaseModel):
    code: str


planner_agent = Agent(
    groq_model,
    system_prompt="""
    Evaluate the user prompt.

    Generate tasks based on descripton. Return List of Task.
    """,
    retries=5,
    result_type=List[Task],
)

gemini_coder_agent = Agent(
    groq_model,
    system_prompt="""
    You are an expert project feature coder.
    Generate clean and maintainable code based on the task.
    """,
    retries=5,
    # result_type=TaskResult
)

ollama_coder_agent = Agent(
    ollama_model,
    system_prompt="You are a python expert, you write clean and maintainable code.",
    retries=5,
    model_settings={
        "max_tokens": 2048,
        "temperature": 0.2,
    },
)


@ollama_coder_agent.tool_plain
def save_to_file(file_name: str, content: str):
    safe_file_name = pathlib.Path(f"{file_name}").name
    file_path = CODING_DIR / safe_file_name

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return f"File saved at {file_path}"
    except Exception as e:
        return f"Error saving file {file_path}: {e}"


gemini_coder_agent = Agent(
    gemini_model,
    system_prompt="""
    You are an expert project feature coder.
    Generate clean and maintainable code based on the task.
    """,
    retries=5,
    # result_type=Union[str, TaskResult]
)


class ProjectService:
    def __init__(self) -> None:
        pass

    def create(self, name: str):
        pass

    def list_files(self):
        pass

    def delete_file(self, file_name: str):
        pass


class AgentService:
    def __init__(self) -> None:
        # task_repo: TaskRepository
        pass

    def save_task_db(self, task: Task):
        pass

    def planner(self, description: str):
        result = planner_agent.run_sync(description)
        return result.data

    def coder_multiple(self, tasks: List[Task]) -> List[TaskResult]:
        results: List[TaskResult] = []

        for task in tasks:
            result = gemini_coder_agent.run_sync(task.description)
            results.append(result.data)

        print("Processed all tasks...")
        return results

    async def coder_single(self, task: str):
        pass

    async def stream_response(self, response):
        pass


async def main():
    agent_service = AgentService()

    task = """
    Create a simple Python script that renders a house using pygame.
    Save file to directory using the save_to_file tool.
    file_name: 'test_house.py'
    """
    chunks: List[str] = []

    try:
        async with ollama_coder_agent.run_stream(task) as first_result:
            print("Streaming response:\n" + "=" * 20)

            async for chunk in first_result.stream():
                print(chunk, end="", flush=True)
                chunks.append(chunk)

            print("\n" + "=" * 20)

        full_response = "".join(chunks)

        print("\n--- Task Streaming Complete ---", file=sys.stderr)
        print(f"Usage: {first_result.usage()}")

    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
