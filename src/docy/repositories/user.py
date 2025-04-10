from sqlalchemy.ext.asyncio.session import AsyncSession

from ..models.user import User
from ..schemas.user import UserIn, UserUpdate
from .base import BaseRepository


class UserRepository(BaseRepository[User, UserIn, UserUpdate]):
    """Repository for user model operations"""

    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
