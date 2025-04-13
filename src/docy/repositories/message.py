from sqlalchemy.ext.asyncio.session import AsyncSession

from ..models.chat import Message
from ..schemas.message import MessageIn, MessageUpdate
from .base import BaseRepository


class MessageRepository(BaseRepository[Message, MessageIn, MessageUpdate]):
    """Repository for Message model operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(Message, session)
