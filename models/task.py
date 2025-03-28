from enum import Enum
from typing import Optional

from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, Text

from models import Base, Agent, Project


class TaskType(str, Enum):
    CODING = "coding"
    WRITING = "writing"


class Task(Base, table=True):
    name: str = Field(index=True)
    description: str = Field(sa_column=Column(Text))
    task_type: TaskType = Field(default=TaskType.CODING, index=True)

    # Relationships
    project_id: int = Field(default=None, foreign_key="projects.id", index=True)
    project: "Project" = Relationship(back_populates="tasks")
    agent_id: Optional[int] = Field(default=None, foreign_key="agents.id", index=True)
    agent: "Agent" = Relationship(back_populates="tasks")

    __tablename__ = "tasks"  # type: ignore


class TaskIn(SQLModel, table=False):
    name: str = Field()
    description: str = Field()
    task_type: TaskType = Field(default=TaskType.CODING)

    # Relationships
    agent_id: Optional[int] = Field(default=None)
    project_id: Optional[int] = Field(default=None)


class TaskOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()
    description: str = Field()
    task_type: TaskType = Field(default=TaskType.CODING)

    # Relationships
    agent: Optional["Agent"] = Field(default=None)
    project: Optional["Project"] = Field(default=None)


class TaskUpdate(SQLModel, table=False):
    name: Optional[str] = Field()
    description: Optional[str] = Field()
    agent: Optional["Agent"] = Field(default=None)
    task_type: Optional[TaskType] = Field(default=None)
