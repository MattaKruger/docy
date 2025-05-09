from typing import List, Optional

from pydantic import BaseModel, Field

from ..models import Artifact, ProjectType, User


class ProjectIn(BaseModel):
    name: str = Field()
    project_type: ProjectType = Field()
    description: Optional[str] = None
    framework: str = Field()

    # Relationships
    user_id: Optional[int] = None


class ProjectOut(BaseModel):
    id: int = Field()
    name: str = Field()

    description: Optional[str] = Field()
    framework: str = Field()
    project_type: ProjectType = Field()

    # Relationships
    user: "User" = Field()
    artifacts: Optional[List["Artifact"]] = Field()


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ProjectType] = None
    description: Optional[str] = None

    # Relationships
    user_id: Optional[int] = None


class ProjectMetadataIn(BaseModel):
    project_id: Optional[int] = Field(default=None)
    languages: Optional[List[str]] = Field(default_factory=list)
    frameworks: Optional[List[str]] = Field(default_factory=list)


class ProjectMetadataOut(BaseModel):
    id: int = Field()

    project_id: Optional[int] = Field(default=None)
    project: Optional[int] = Field(default=None)
