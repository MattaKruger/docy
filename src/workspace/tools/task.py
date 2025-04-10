from typing import List

from pydantic import BaseModel, Field


class Task(BaseModel):
    name: str = Field(default="")
    content: str = Field(default="")
    agent: str = Field(default="ollama")


class TaskResult(Task):
    generated: str = Field(default="")


tasks: List[Task] = []


def get_task(task_id: int) -> Task:
    return Task(name="Fastapi main.py", content="Create a simple fastapi application")


def get_tasks() -> List[Task]:
    return tasks


def add_task(task: Task) -> Task:
    tasks.append(task)
    return task


def handle_task(task: Task) -> TaskResult:
    current_task = task
    current_agent = task.agent

    output = "TETSTST"

    return TaskResult(
        name=current_task.name,
        content=current_task.content,
        agent=current_agent,
        generated=output,
    )


exported_tools = {"handle_task": handle_task, "get_task": get_task, "add_task": add_task}
