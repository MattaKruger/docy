from .base import BaseRepository
from sqlmodel import Session

from models import Task


class TaskRepository(BaseRepository):
    """Repository for handling task model operations"""

    def __init__(self, session: Session):
        super().__init__(Task, session)
