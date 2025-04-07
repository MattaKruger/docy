from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio.session import AsyncSession

from matter.schemas import ProjectIn, ProjectUpdate, ProjectOut
from matter.db import get_session

from matter.repositories import ProjectRepository

router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_repo(session: AsyncSession = Depends(get_session)) -> ProjectRepository:
    return ProjectRepository(session)


@router.get("/", response_model=List[ProjectOut])
async def get_projects(project_repo: ProjectRepository = Depends(get_project_repo)):
    return await project_repo.get_multi()


@router.get("/{project_id}", response_model=ProjectOut)
async def get_project(project_id: int = Path(...), project_repo: ProjectRepository = Depends(get_project_repo)):
    return await project_repo.get(project_id)


@router.post("/")
async def create_project(project: ProjectIn, project_repo: ProjectRepository = Depends(get_project_repo)):
    return await project_repo.create(project)


@router.put("/{project_id}")
async def update_project(
    project: ProjectUpdate, project_id: int = Path(...), project_repo: ProjectRepository = Depends(get_project_repo)
):
    return await project_repo.update(project_id, project)
