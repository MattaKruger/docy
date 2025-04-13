from typing import List, Optional

from pydantic import BaseModel, Field

from ..models import Agent, Category, Project


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
    category: Category = Field()

    # Relationships
    subtasks: List["SubTaskOut"] = []
    agent: Optional["Agent"] = Field(default=None)
    project: Optional["Project"] = Field(default=None)


class TaskUpdate(BaseModel):
    name: Optional[str] = Field(default=None)
    description: Optional[str] = Field(default=None)
    task_type: Optional[Category] = Field(default=None)


class SubTaskIn(BaseModel):
    name: str = Field()
    description: str = Field()
    is_completed: bool = Field(default=False)
    task_id: int = Field()
    agent_id: Optional[int] = Field(default=None)


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
