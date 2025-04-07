from sqlmodel import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from ..models.artifact import Artifact
from ..schemas.artifact import ArtifactIn, ArtifactOut, ArtifactUpdate

from .base import BaseRepository


class ArtifactRepository(BaseRepository[Artifact, ArtifactIn, ArtifactUpdate]):
    """Repository for ProjectArtifact model operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(Artifact, session)
