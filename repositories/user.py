from sqlmodel.ext.asyncio import AsyncSession

from models import User, UserIn, UserUpdate

from .base import BaseRepository


class UserRepository(BaseRepository[User, UserIn, UserUpdate]):
    """Repository for user model operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
