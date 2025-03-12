from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from .base import Base
from .user import User


class ProjectType(Enum, str):
    DEFAULT = "default"
    CODE = "code"


class Project(Base, table=True):
    pass


class ProjectOut(SQLModel, table=False):
    id: int
    name: str
    type: ProjectType
    description: Optional[str] = None
    owner_id: Optional[int] = None
    owner: Optional["User"] = Relationship(back_populates="projects")


class ProjectIn(SQLModel):
    name: str
    type: ProjectType
    description: Optional[str] = None
    owner_id: Optional[int] = None
