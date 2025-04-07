from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio.session import AsyncSession

from matter.db.session import get_session
from matter.schemas import PromptIn, PromptUpdate
from matter.repositories import PromptRepository


router = APIRouter(prefix="/prompts", tags=["prompts"])


def get_prompt_repo(session: AsyncSession = Depends(get_session)) -> PromptRepository:
    return PromptRepository(session)


@router.get("/")
async def get_prompts(repo: PromptRepository = Depends(get_prompt_repo)):
    return await repo.get_multi()


@router.get("/{prompt_id}")
async def get_prompt(prompt_id: int = Path(...), prompt_repo=Depends(get_prompt_repo)):
    return await prompt_repo.get(prompt_id)


@router.post("/")
async def create_prompt(prompt: PromptIn, prompt_repo: PromptRepository = Depends(get_prompt_repo)):
    return await prompt_repo.create(prompt)


@router.put("/{prompt_id}")
async def update_prompt(
    prompt: PromptUpdate, prompt_id: int = Path(...), prompt_repo: PromptRepository = Depends(get_prompt_repo)
):
    return await prompt_repo.update(prompt_id, prompt)
