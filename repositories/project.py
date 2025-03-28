from typing import Optional
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlmodel import select

from .base import BaseRepository
from models import Project, ProjectIn, ProjectUpdate


class ProjectRepository(BaseRepository[Project, ProjectIn, ProjectUpdate]):
    """Repository for project model operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def get_by_name(self, name: str) -> Optional[Project]:
        """Gets a project by its unique name"""
        statement = select(Project).where(Project.name == name)
        results = await self.session.exec(statement)
        return results.first()

    async def get_by_owner(self, owner_id: int) -> Optional[Project]:
        """Gets a project by its owner"""
        statement = select(Project).where(Project.owner_id == owner_id)
        results = await self.session.exec(statement)
        return results.first()
