from sqlmodel.ext.asyncio.session import AsyncSession


from .base import BaseRepository
from models import User, UserIn, UserUpdate


class UserRepository(BaseRepository[User, UserIn, UserUpdate]):
    """Repository for user model operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
