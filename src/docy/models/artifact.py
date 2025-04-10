from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Column, Field, Relationship, Text

from .base import Base

if TYPE_CHECKING:
    from .chat import Message
    from .project import Project


class ArtifactType(str, Enum):
    DEFAULT = "default"
    CODE = "code"
    MARKDOWN = "markdown"


class Artifact(Base, table=True):
    __tablename__ = "artifacts"  # type: ignore

    name: str = Field(index=True)
    description: str = Field(sa_column=Column(Text))
    content: str = Field(sa_column=Column(Text))
    validated: bool = Field(default=False, index=True)
    artifact_type: ArtifactType = Field(default=ArtifactType.DEFAULT, index=True)

    # Relationships
    project_id: int = Field(foreign_key="projects.id")
    project: "Project" = Relationship(back_populates="artifacts", sa_relationship_kwargs=dict(lazy="selectin"))
    message: Optional["Message"] = Relationship(back_populates="artifact", sa_relationship_kwargs=dict(lazy="selectin"))
