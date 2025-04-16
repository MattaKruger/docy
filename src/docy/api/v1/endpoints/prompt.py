from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio.session import AsyncSession

from docy.db.session import get_session
from docy.repositories import PromptRepository
from docy.models import Prompt
from docy.schemas import PromptIn, PromptUpdate, PromptOut

router = APIRouter(prefix="/prompts", tags=["prompts"])


def get_prompt_repo(session: AsyncSession = Depends(get_session)) -> PromptRepository:
    return PromptRepository(session)


@router.get("/", response_model=list[Prompt])
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
    prompt_update: PromptUpdate, prompt_id: int = Path(...), prompt_repo: PromptRepository = Depends(get_prompt_repo)
):
    prompt_db = await prompt_repo.get_or_404(prompt_id)
    return await prompt_repo.update(prompt_update, prompt_db)
