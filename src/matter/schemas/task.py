from typing import Optional

from pydantic import BaseModel, Field

from ..models import Agent, Project, TaskType


class TaskIn(BaseModel):
    name: str = Field()
    description: str = Field()
    task_type: TaskType = Field(default=TaskType.CODING)

    # Relationships
    agent_id: Optional[int] = Field(default=None)
    project_id: Optional[int] = Field(default=None)


class TaskOut(BaseModel):
    id: int = Field()
    name: str = Field()
    description: str = Field()
    task_type: TaskType = Field()

    # Relationships
    agent: Optional["Agent"] = Field(default=None)
    project: Optional["Project"] = Field(default=None)


class TaskUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    task_type: Optional[TaskType] = Field(default=None)
