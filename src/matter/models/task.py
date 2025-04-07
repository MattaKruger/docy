from enum import Enum
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .agent import Agent
    from .project import Project


class TaskType(str, Enum):
    CODING = "coding"
    WRITING = "writing"


class Task(Base, table=True):
    __tablename__ = "tasks"  # type: ignore

    name: str = Field(index=True)
    description: str = Field(sa_column=Column(Text))
    task_type: TaskType = Field(default=TaskType.CODING, index=True)

    # Relationships
    project_id: int = Field(foreign_key="projects.id", index=True)
    project: "Project" = Relationship(back_populates="tasks")
    agent_id: Optional[int] = Field(default=None, foreign_key="agents.id", index=True)
    agent: Optional["Agent"] = Relationship(back_populates="tasks")
