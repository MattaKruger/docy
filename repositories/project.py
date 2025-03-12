from typing import List, Type

from .base import BaseRepository
from sqlmodel import Session
from models import Project


class ProjectRepository(BaseRepository):
    """Repository for project model operations"""
    def __init__(self, model: Type[Project], session: Session):
        super().__init__(model, session)
