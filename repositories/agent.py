from typing import Optional
from fastapi import HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from repositories.prompt import PromptRepository

from .base import BaseRepository
from models import Agent, AgentIn, AgentUpdate, Prompt, AgentState


class AgentRepository(BaseRepository[Agent, AgentIn, AgentUpdate]):
    """Repository for agent model operations"""

    def __init__(self, session: AsyncSession, prompt_repo: PromptRepository):
        super().__init__(Agent, session)
        self.prompt_repo = prompt_repo

    async def create(self, agent_in: AgentIn) -> Agent:
        """Creates a new agent, ensuring the associated prompt exists."""
        print(f"Attempting to create agent: {agent_in.name}")

        prompt = await self.prompt_repo.get(agent_in.system_prompt_id)
        if not prompt:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"System prompt with ID {agent_in.system_prompt_id} not found.",
            )
        agent = Agent.model_validate(agent_in)
        self.session.add(agent)
        await self.session.commit()
        await self.session.refresh(agent)
        print(
            f"Succesfully created Agent ID: {agent.id} - '{agent.name}', linked to Prompt ID: {agent.system_prompt_id}"
        )

        return agent

    async def get_active_agent(self, agent_id: int) -> Optional[Agent]:
        """Gets an agent by ID only if their state is ACTIVE"""
        statement = select(Agent).where(Agent.id == agent_id, Agent.state == AgentState.ACTIVE)
        agent = await self.session.execute(statement)
        return agent.scalar_one_or_none()
