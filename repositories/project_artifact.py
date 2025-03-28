from sqlmodel.ext.asyncio.session import AsyncSession

from models import (
    ProjectArtifact,
    ProjectArtifactIn,
    ProjectArtifactUpdate,
)
from .base import BaseRepository


class ProjectArtifactRepository(BaseRepository[ProjectArtifact, ProjectArtifactIn, ProjectArtifactUpdate]):
    """Repository for ProjectArtifact model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(ProjectArtifact, session)
