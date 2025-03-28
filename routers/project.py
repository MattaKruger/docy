from fastapi import Path, Depends, APIRouter

from database.db import get_session, Session
from models import ProjectIn, ProjectUpdate, ProjectArtifact
from repositories import ProjectRepository


router = APIRouter(prefix="/projects", tags=["projects"])


def get_project_repo(session: Session = Depends(get_session)) -> ProjectRepository:
    return ProjectRepository(session)


@router.get("/")
async def get_projects(project_repo: ProjectRepository = Depends(get_project_repo)):
    return await project_repo.get_multi()


@router.get("/{project_id}")
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
