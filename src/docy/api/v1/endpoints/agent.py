from typing import List

from fastapi import APIRouter, Depends, Path
from sqlalchemy.ext.asyncio.session import AsyncSession

from docy.db import get_session
from docy.models import AgentState
from docy.repositories import AgentRepository, PromptRepository
from docy.schemas import AgentIn, AgentOut, AgentUpdate

router = APIRouter(prefix="/agents", tags=["agents"])


def get_agent_repo(session: AsyncSession = Depends(get_session)) -> AgentRepository:
    return AgentRepository(session, prompt_repo=PromptRepository(session))


@router.get("/", response_model=List[AgentOut])
async def get_agents(agent_repo: AgentRepository = Depends(get_agent_repo)):
    return await agent_repo.get_multi()


@router.post("/")
async def create_agent(agent: AgentIn, agent_repo: AgentRepository = Depends(get_agent_repo)):
    return await agent_repo.create(agent)


@router.get("/{agent_id}")
async def get_agent(agent_id: int = Path(...), agent_repo: AgentRepository = Depends(get_agent_repo)):
    return await agent_repo.get(agent_id)


@router.put("/{agent_id}")
async def update_agent(
    agent_update: AgentUpdate, agent_id: int = Path(...), agent_repo: AgentRepository = Depends(get_agent_repo)
):
    agent_db = await agent_repo.get_or_404(agent_id)
    return await agent_repo.update(agent_update, agent_db)


@router.get("/active")
async def get_active_agents(agent_repo: AgentRepository = Depends(get_agent_repo)):
    return await agent_repo.get_multi(filters={"state": AgentState.ACTIVE})
