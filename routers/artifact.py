from fastapi import APIRouter, Depends
from repositories import ProjectArtifactRepository
from database import engine, get_session, Session
from models import ProjectArtifactIn, ProjectArtifactUpdate, ProjectArtifact


router = APIRouter(prefix="/artifacts", tags=["artifacts"])


def get_project_artifact_repository(session: Session = Depends(get_session)):
    return ProjectArtifactRepository(session)


@router.get("/")
async def get_artifacts(project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository)):
    return await project_artifact_repo.get_multi()


@router.post("/")
async def create_artifact(
    project_artifact: ProjectArtifactIn,
    project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository),
):
    return await project_artifact_repo.create(project_artifact)


@router.put("/{id}")
async def update_artifact(
    id: int,
    project_artifact: ProjectArtifactUpdate,
    project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository),
):
    return await project_artifact_repo.update(id, project_artifact)


@router.delete("/{id}")
async def delete_artifact(
    id: int,
    project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository),
):
    return await project_artifact_repo.delete(id)


@router.get("/{id}")
async def get_artifact(
    id: int,
    project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository),
):
    return await project_artifact_repo.get(id)
