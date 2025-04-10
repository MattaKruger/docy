from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select

from ..models.chat import Chat, Message
from ..schemas.chat import ChatIn, ChatUpdate
from .base import BaseRepository


class ChatRepository(BaseRepository[Chat, ChatIn, ChatUpdate]):
    """Repository for Chat model operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(Chat, session)

    async def get_messages_by_chat_id(self, chat_id: int):
        return await self.session.execute(select(Message).where(Message.chat_id == chat_id))

    async def get_messages_by_message_type(self, chat_id: int, message_type: str):
        return await self.session.execute(
            select(Message).where(Message.chat_id == chat_id).where(Message.message_type == message_type)
        )
