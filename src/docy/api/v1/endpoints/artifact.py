from typing import List

from fastapi import APIRouter, Depends, Path, status
from fastapi.exceptions import HTTPException
from sqlalchemy.ext.asyncio.session import AsyncSession

from docy.db import get_session
from docy.repositories import ArtifactRepository
from docy.schemas.artifact import ArtifactIn, ArtifactOut, ArtifactUpdate

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


def get_artifact_repository(session: AsyncSession = Depends(get_session)):
    return ArtifactRepository(session)


@router.get("/", response_model=List[ArtifactOut])
async def get_artifacts(artifact_repo: ArtifactRepository = Depends(get_artifact_repository)):
    artifacts = await artifact_repo.get_multi()
    return artifacts


@router.get("/{artifact_id}", response_model=ArtifactOut)
async def get_artifact(
    artifact_id: int = Path(...),
    artifact_repo: ArtifactRepository = Depends(get_artifact_repository),
):
    artifact = await artifact_repo.get_or_404(artifact_id)
    return artifact


@router.post("/", response_model=int)
async def create_artifact(
    project_artifact: ArtifactIn,
    artifact_repo: ArtifactRepository = Depends(get_artifact_repository),
):
    artifact = await artifact_repo.create(project_artifact)
    return artifact.id


@router.put("/{artifact_id}")
async def update_artifact(
    artifact_update: ArtifactUpdate,
    artifact_id: int = Path(...),
    artifact_repo: ArtifactRepository = Depends(get_artifact_repository),
):
    artifact_db = await artifact_repo.get_or_404(artifact_id)

    updated_artifact = await artifact_repo.update(artifact_update, artifact_db)
    if updated_artifact is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update artifact")

    return updated_artifact


@router.delete("/{artifact_id}")
async def delete_artifact(
    artifact_id: int = Path(...),
    artifact_repo: ArtifactRepository = Depends(get_artifact_repository),
):
    return await artifact_repo.delete(artifact_id)
