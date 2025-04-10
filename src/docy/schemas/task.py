from typing import Optional, List
from pydantic import BaseModel, Field

from ..models import Agent, Project, Category


class TaskIn(BaseModel):
    name: str = Field()
    description: str = Field()
    task_type: Category = Field(default=Category.CODING)

    # Relationships
    agent_id: Optional[int] = Field(default=None)
    project_id: Optional[int] = Field(default=None)
    subtasks: Optional[List["SubTaskIn"]] = Field(default=None)


class TaskOut(BaseModel):
    id: int = Field()
    name: str = Field()
    description: str = Field()
    task_type: Category = Field()

    # Relationships
    agent: Optional["Agent"] = Field(default=None)
    project: Optional["Project"] = Field(default=None)
    subtasks: List["SubTaskOut"] = []


class TaskUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    task_type: Optional[Category] = Field(default=None)


class SubTaskIn(BaseModel):
    name: str = Field()
    description: str = Field()
    is_completed: bool = Field(default=False)
    task_id: int = Field()


class SubTaskOut(BaseModel):
    id: int = Field()
    name: str = Field()
    description: str = Field()
    is_completed: bool = Field()
    task: "TaskOut" = Field()


class SubTaskUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    is_completed: Optional[bool] = Field(default=None)
