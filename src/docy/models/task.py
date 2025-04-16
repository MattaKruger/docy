from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .agent import Agent
    from .chat import Message
    from .project import Project


class Category(str, Enum):
    CODING = "coding"
    WRITING = "writing"
    PLANNING = "planning"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ERROR = "ERROR"


class SubTask(Base, table=True):
    __tablename__ = "subtasks"  # type: ignore

    name: str = Field(index=True)
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)
    is_completed: bool = Field(default=False, index=True)

    task_id: int = Field(foreign_key="tasks.id", index=True)
    task: "Task" = Relationship(back_populates="subtasks", sa_relationship_kwargs=dict(lazy="selectin"))
    agent_id: Optional[int] = Field(default=None, foreign_key="agents.id", index=True)
    agent: Optional["Agent"] = Relationship(back_populates="subtasks", sa_relationship_kwargs=dict(lazy="selectin"))


class Task(Base, table=True):
    __tablename__ = "tasks"  # type: ignore

    name: str = Field(index=True)
    description: str = Field(sa_column=Column(Text))
    category: Category = Field(default=Category.CODING, index=True)
    status: TaskStatus = Field(default=TaskStatus.PENDING, index=True)

    agent_id: Optional[int] = Field(default=None, foreign_key="agents.id", index=True)
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id", index=True)
    agent: Optional["Agent"] = Relationship(back_populates="tasks", sa_relationship_kwargs=dict(lazy="selectin"))
    project: Optional["Project"] = Relationship(back_populates="tasks", sa_relationship_kwargs=dict(lazy="selectin"))

    # messages: List["Message"] = Relationship(
    #     back_populates="task", sa_relationship_kwargs=dict(lazy="selectin", cascade="all, delete-orphan")
    # )
    subtasks: List["SubTask"] = Relationship(
        back_populates="task", sa_relationship_kwargs=dict(lazy="selectin", cascade="all, delete-orphan")
    )

    @property
    def assigned(self) -> bool:
        return self.agent_id is not None
