from enum import Enum
from typing import TYPE_CHECKING, Optional, List

from sqlalchemy import Column, Text
from sqlalchemy.ext.hybrid import hybrid_property
from sqlmodel import Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .agent import Agent
    from .project import Project
    from .chat import Message


class Category(str, Enum):
    CODING = "coding"
    WRITING = "writing"
    PLANNING = "planning"


class SubTask(Base, table=True):
    __tablename__ = "subtasks"  # type: ignore

    name: str = Field(index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_completed: bool = Field(default=False, index=True)

    task_id: int = Field(foreign_key="tasks.id", index=True)
    task: "Task" = Relationship(back_populates="subtasks", sa_relationship_kwargs=dict(lazy="selectin"))

    # TODO
    # Add agent_id/agent if needed, might be nice if subtask requires different agent.


class Task(Base, table=True):
    __tablename__ = "tasks"  # type: ignore

    name: str = Field(index=True)
    description: str = Field(sa_column=Column(Text))
    category: Category = Field(default=Category.CODING, index=True)

    project_id: int = Field(foreign_key="projects.id", index=True)
    project: "Project" = Relationship(back_populates="tasks", sa_relationship_kwargs=dict(lazy="selectin"))
    agent_id: Optional[int] = Field(default=None, foreign_key="agents.id", index=True)
    agent: Optional["Agent"] = Relationship(back_populates="tasks", sa_relationship_kwargs=dict(lazy="selectin"))
    messages: List["Message"] = Relationship(
        back_populates="task", sa_relationship_kwargs=dict(lazy="selectin", cascade="all, delete-orphan")
    )
    subtasks: List["SubTask"] = Relationship(
        back_populates="task", sa_relationship_kwargs=dict(lazy="selectin", cascade="all, delete-orphan")
    )

    @property
    def assigned(self) -> bool:
        return self.agent_id is not None
