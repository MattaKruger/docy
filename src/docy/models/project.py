from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, String, Text
from sqlalchemy.dialects.postgresql import ARRAY
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
    __tablename__ = "projects"  # type: ignore

    name: str = Field(unique=True, index=True)
    project_type: ProjectType = Field(default=ProjectType.DEFAULT, index=True)
    description: str = Field(sa_column=Column(Text))
    framework: str = Field(index=True)

    # Relationships
    user_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    user: Optional["User"] = Relationship(back_populates="projects", sa_relationship_kwargs=dict(lazy="selectin"))
    tasks: List["Task"] = Relationship(back_populates="project", sa_relationship_kwargs=dict(lazy="selectin"))
    artifacts: List["Artifact"] = Relationship(back_populates="project", sa_relationship_kwargs=dict(lazy="selectin"))


class ProjectMetadata(Base, table=True):
    __tablename__ = "project_metadata"  # type: ignore

    project_id: Optional[int] = Field(default=None, foreign_key="projects.id")
    languages: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
    frameworks: Optional[List[str]] = Field(default=None, sa_column=Column(ARRAY(String)))
