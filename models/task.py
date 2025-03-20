from enum import Enum
from sqlmodel import Field, Relationship, SQLModel
from typing import Optional
from models import Base, Agent


class TaskType(str, Enum):
    CODING = "coding"
    WRITING = "writing"


class Task(Base, table=True):
    name: str = Field()
    description: str = Field()

    # Relationships
    agent_id: int = Field(default=None, foreign_key="agents.id")
    # agent: "Agent" = Relationship(back_populates="task")

    __tablename__ = "tasks"  # type: ignore


class TaskIn(SQLModel, table=False):
    name: str = Field()
    description: str = Field()

    # Relationships
    agent_id: Optional[int] = Field(default=None)


class TaskOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()
    description: str = Field()

    # Relationships
    agent: Optional["Agent"] = Field(default=None)


class TaskUpdate(SQLModel, table=False):
    name: Optional[str] = Field()
    description: Optional[str] = Field()
    agent: Optional["Agent"] = Field(default=None)
