from .base import BaseRepository
from sqlmodel import Session
from models import Agent


class AgentRepository(BaseRepository):
    """Repoistory for agent model operations"""

    def __init__(self, session: Session):
        super().__init__(Agent, session)
