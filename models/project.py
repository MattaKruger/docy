from ssl import Options
from typing import TYPE_CHECKING

from enum import Enum
from typing import Optional, List
from rich.color import Color
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, Text

from .base import Base

from .user import User
from .task import Task


class ProjectType(str, Enum):
    DEFAULT = "default"
    CODE = "code"


class Project(Base, table=True):
    name: str = Field(unique=True, index=True)
    project_type: ProjectType = Field(default=ProjectType.DEFAULT, index=True)
    description: str = Field(sa_column=Column(Text))
    framework: str = Field()

    # Relationships
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id", index=True)
    owner: Optional["User"] = Relationship(back_populates="projects")
    artifacts: List["ProjectArtifact"] = Relationship(back_populates="project")
    tasks: List["Task"] = Relationship(back_populates="project")

    __tablename__ = "projects"  # type:ignore


class ProjectOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()

    description: Optional[str] = Field()
    framework: str = Field()
    project_type: ProjectType = Field()

    # Relationships
    owner_id: Optional[int] = None


class ProjectIn(SQLModel, table=False):
    name: str = Field()
    project_type: ProjectType = Field()
    description: Optional[str] = None
    framework: str = Field()

    # Relationships
    owner_id: Optional[int] = None


class ProjectUpdate(SQLModel, table=False):
    name: Optional[str] = None
    type: Optional[ProjectType] = None
    description: Optional[str] = None

    # Relationships
    owner_id: Optional[int] = None


class ProjectArtifactType(str, Enum):
    DEFAULT = "default"
    CODE = "code"
    MARKDOWN = "markdown"


class ProjectArtifact(Base, table=True):
    name: str = Field(index=True)
    description: str = Field(sa_column=Column(Text))
    content: str = Field(sa_column=Column(Text))
    validated: bool = Field(default=False, index=True)
    project_artifact_type: ProjectArtifactType = Field(default=ProjectArtifactType.DEFAULT, index=True)

    # Relationships
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id")
    project: Optional[Project] = Relationship(back_populates="artifacts")

    __tablename__ = "project_artifacts"  # type: ignore


class ProjectArtifactIn(SQLModel, table=False):
    name: str = Field()
    description: str = Field()
    content: str = Field()
    validated: bool = Field(default=False)

    project_artifact_type: ProjectArtifactType = Field(default=ProjectArtifactType.DEFAULT)

    # Relationships
    project_id: Optional[int] = Field(default=None)


class ProjectArtifactOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()
    description: str = Field()
    content: str = Field()
    validated: bool = Field()
    project_artifact_type: ProjectArtifactType = Field()

    # Relationships
    project_id: Optional[int] = None


class ProjectArtifactUpdate(SQLModel, table=False):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    validated: Optional[bool] = None

    project_artifact_type: Optional[ProjectArtifactType] = None

    # Relationships
    project_id: Optional[int] = None
