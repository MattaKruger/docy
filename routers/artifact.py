from fastapi import APIRouter, Depends, Path

from database import get_session
from models import ProjectArtifactIn, ProjectArtifactUpdate
from repositories import ProjectArtifactRepository

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


def get_project_artifact_repository():
    return ProjectArtifactRepository(Depends(get_session))


@router.get("/")
async def get_artifacts(project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository)):
    return await project_artifact_repo.get_multi()


@router.post("/")
async def create_artifact(
    project_artifact: ProjectArtifactIn,
    project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository),
):
    return await project_artifact_repo.create(project_artifact)


@router.put("/{artifact_id}")
async def update_artifact(
    project_artifact: ProjectArtifactUpdate,
    artifact_id: int = Path(...),
    project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository),
):
    return await project_artifact_repo.update(artifact_id, project_artifact)


@router.delete("/{artifact_id}")
async def delete_artifact(
    artifact_id: int = Path(...),
    project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository),
):
    return await project_artifact_repo.delete(artifact_id)


@router.get("/{artifact_id}")
async def get_artifact(
    artifact_id: int = Path(...),
    project_artifact_repo: ProjectArtifactRepository = Depends(get_project_artifact_repository),
):
    return await project_artifact_repo.get(artifact_id)
