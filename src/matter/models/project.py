from enum import Enum
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, Text
from sqlmodel import Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .artifact import Artifact
    from .task import Task
    from .user import User


class ProjectType(str, Enum):
    DEFAULT = "default"
    CODE = "code"


class Project(Base, table=True):
    __tablename__ = "projects"  # type:ignore

    name: str = Field(unique=True, index=True)
    project_type: ProjectType = Field(default=ProjectType.DEFAULT, index=True)
    description: str = Field(sa_column=Column(Text))
    framework: str = Field()

    # Relationships
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    user: Optional["User"] = Relationship(back_populates="projects")
    artifacts: List["Artifact"] = Relationship(back_populates="project")
    tasks: List["Task"] = Relationship(back_populates="project")
