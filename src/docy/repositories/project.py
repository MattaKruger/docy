from typing import Optional, List


from sqlmodel import select, any_
from sqlalchemy.ext.asyncio.session import AsyncSession


from ..models.project import Project, ProjectMetadata
from ..schemas.project import ProjectIn, ProjectUpdate, ProjectMetadataIn
from .base import BaseRepository


class ProjectRepository(BaseRepository[Project, ProjectIn, ProjectUpdate]):
    """Repository for project model operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(Project, session)

    async def create_project_with_metadata(self, project: Project) -> Optional[Project]:
        """Create a project based on metadata"""
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def get_all_by_id(self, project_id: int) -> Optional[List[Project]]:
        """Gets a project by its unique id"""
        statement = select(Project).where(Project.id == project_id)
        results = await self.session.execute(statement)
        return list(results.scalars().all())

    async def get_all_by_name(self, name: str) -> Optional[List[Project]]:
        """Gets a project by its unique name"""
        statement = select(Project).where(Project.name == name)
        results = await self.session.execute(statement)
        return list(results.scalars().all())

    async def get_all_by_language(self, language: str) -> Optional[List[Project]]:
        """Gets all projects associated with a programming language"""
        statement = select(Project).where(any_(Project.project_metadata.languages) == language)
        results = await self.session.execute(statement)
        return list(results.scalars().all())

    async def get_all_by_framework(self, framework: str) -> Optional[List[Project]]:
        """Gets all projects associated with a framework"""
        statement = select(Project).where(any_(Project.project_metadata.frameworks) == framework)
        results = await self.session.execute(statement)
        return list(results.scalars().all())

    async def get_all_by_user(self, user_id: int) -> Optional[List[Project]]:
        """Gets a project by its user"""
        statement = select(Project).where(Project.user_id == user_id)
        results = await self.session.execute(statement)
        return list(results.scalars().all())
