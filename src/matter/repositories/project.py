from typing import Optional

from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from ..models.project import Project
from ..schemas.project import ProjectIn, ProjectUpdate

from .base import BaseRepository


class ProjectRepository(BaseRepository[Project, ProjectIn, ProjectUpdate]):
    """Repository for project model operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def get(self, id: int) -> Project | None:
        """ """
        statement = select(self.model).where(self.model.id == id)
        statement = statement.options(joinedload(self.model.user))
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_name(self, name: str) -> Optional[Project]:
        """Gets a project by its unique name"""
        statement = select(Project).where(Project.name == name)
        results = await self.session.execute(statement)
        return results.scalar()

    async def get_by_owner(self, user_id: int) -> Optional[Project]:
        """Gets a project by its owner"""
        statement = select(Project).where(Project.user_id == user_id)
        results = await self.session.execute(statement)
        return results.scalar()
