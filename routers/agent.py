# from pydantic_ai import Agent
# from pydantic_ai.models.groq import GroqModel

import logfire
from typing import List
from fastapi import APIRouter, Depends, Path
from database import get_session, Session

from repositories import AgentRepository
from models import AgentIn, AgentUpdate, AgentOut, AgentState


logfire.configure()
# Agent.instrument_all()

router = APIRouter(prefix="/agent", tags=["agent"])


def get_agent_repo(session: Session = Depends(get_session)) -> AgentRepository:
    return AgentRepository(session)


@router.get("/", response_model=List[AgentOut])
async def get_agents(agent_repo: AgentRepository = Depends(get_agent_repo)):
    return await agent_repo.get_multi()


@router.get("/{agent_id}")
async def get_agent(agent_id: int = Path(...), agent_repo: AgentRepository = Depends(get_agent_repo)):
    return await agent_repo.get(agent_id)


@router.post("/")
async def create_agent(agent: AgentIn, agent_repo: AgentRepository = Depends(get_agent_repo)):
    return await agent_repo.create(agent)


@router.put("/{agent_id}")
async def update_agent(
    agent: AgentUpdate, agent_id: int = Path(...), agent_repo: AgentRepository = Depends(get_agent_repo)
):
    return await agent_repo.update(agent_id, agent)


@router.get("/active")
async def get_active_agents(agent_repo: AgentRepository = Depends(get_agent_repo)):
    return await agent_repo.get_multi(filters={"state": AgentState.ACTIVE})
