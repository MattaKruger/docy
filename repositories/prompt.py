from typing import Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel.main import SQLModel

from .base import BaseRepository
from models import Prompt, PromptIn, PromptOut


class PromptUpdate(SQLModel):
    name: Optional[str] = None


class PromptRepository(BaseRepository[Prompt, PromptIn, PromptUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(Prompt, session)

    async def get_by_name(self, name: str) -> Optional[Prompt]:
        """Gets a prompt by its name"""
        statement = select(Prompt).where(Prompt.name == name)
        result = await self.session.exec(statement)
        return result.first()

    async def get_or_create(self, name: str, content: str) -> Prompt:
        """Gets a prompt by name, creating it if it doesnt exist"""
        prompt = await self.get_by_name(name)
        if not prompt:
            prompt_in = PromptIn(name=name, content=content)
            prompt = await self.create(prompt_in)
            print(f"Created prompt ID: {prompt.id}")
        return prompt
