from typing import List

from fastapi import APIRouter, Depends, Path, status
from fastapi.exceptions import HTTPException

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from matter.db import get_session

from matter.models import Artifact
from matter.repositories import ArtifactRepository
from matter.schemas.artifact import ArtifactIn, ArtifactOut, ArtifactUpdate

router = APIRouter(prefix="/artifacts", tags=["artifacts"])


def artifact_repository(session: AsyncSession = Depends(get_session)):
    return ArtifactRepository(session)


@router.get("/", response_model=List[ArtifactOut])
async def get_artifacts(artifact_repo: ArtifactRepository = Depends(artifact_repository)):
    artifacts = await artifact_repo.get_multi()
    return artifacts


@router.get("/{artifact_id}", response_model=ArtifactOut)
async def get_artifact(
    artifact_id: int = Path(...),
    artifact_repo: ArtifactRepository = Depends(artifact_repository),
):
    load_options = [joinedload(Artifact.project)]
    artifact = await artifact_repo.get_or_404(artifact_id, load_options=load_options)
    return artifact


@router.post("/", response_model=int)
async def create_artifact(
    project_artifact: ArtifactIn,
    artifact_repo: ArtifactRepository = Depends(artifact_repository),
):
    artifact = await artifact_repo.create(project_artifact)
    return artifact.id

@router.put("/{artifact_id}")
async def update_artifact(
    artifact_update: ArtifactUpdate,
    artifact_id: int = Path(...),
    artifact_repo: ArtifactRepository = Depends(artifact_repository),
):
    artifact_db = await artifact_repo.get_or_404(artifact_id)

    updated_artifact = await artifact_repo.update(artifact_update, artifact_db)
    if updated_artifact is None:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update artifact")

    return updated_artifact


@router.delete("/{artifact_id}")
async def delete_artifact(
    artifact_id: int = Path(...),
    artifact_repo: ArtifactRepository = Depends(artifact_repository),
):
    return await artifact_repo.delete(artifact_id)
