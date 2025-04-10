from typing import Optional

from pydantic import BaseModel, Field

from ..models import ArtifactType, Project


class ArtifactIn(BaseModel):
    name: str = Field()
    description: str = Field()
    content: str = Field()
    validated: bool = Field(default=False)

    artifact_type: ArtifactType = Field(default=ArtifactType.DEFAULT)

    # Relationships
    project_id: Optional[int] = Field(default=None)


class ArtifactOut(BaseModel):
    id: int = Field()
    name: str = Field()
    description: str = Field()
    content: str = Field()
    validated: bool = Field()
    artifact_type: ArtifactType = Field()

    # Relationships
    project: Optional["Project"] = Field()


class ArtifactUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    validated: Optional[bool] = None

    artifact_type: Optional[ArtifactType] = None

    # Relationships
    project_id: Optional[int] = None
