from typing import TYPE_CHECKING

from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from .base import Base


if TYPE_CHECKING:
    from .user import User


class ProjectType(str, Enum):
    DEFAULT = "default"
    CODE = "code"


class Project(Base, table=True):
    name: str = Field(unique=True)
    project_type: ProjectType = Field(default=ProjectType.DEFAULT)
    description: str = Field()
    framework: str = Field()

    # Relationships
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
    owner: "User" = Relationship(back_populates="projects")
    artifacts: list["ProjectArtifact"] = Relationship(back_populates="project")

    __tablename__ = "projects"  # type:ignore


class ProjectOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()
    project_type: ProjectType = Field()
    description: Optional[str] = None

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
    name: str = Field(unique=True)
    description: str = Field()
    content: str = Field()
    validated: bool = Field(default=False)
    project_artifact_type: ProjectArtifactType = Field(default=ProjectArtifactType.DEFAULT)

    # Relationships
    project_id: Optional[int] = Field(default=None, foreign_key="projects.id")
    project: Project = Relationship(back_populates="artifacts")


class ProjectArtifactIn(SQLModel, table=False):
    name: str = Field()
    description: str = Field()
    content: str = Field()
    validated: bool = Field(default=False)

    project_artifact_type: ProjectArtifactType = Field(default=ProjectArtifactType.DEFAULT)

    # Relationships
    project_id: Optional[int] = None


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
