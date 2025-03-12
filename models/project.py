from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from .base import Base
from .user import User


class ProjectType(Enum, str):
    DEFAULT = "default"
    CODE = "code"


class Project(Base, table=True):
    name: str = Field()
    project_type: ProjectType = Field(default=ProjectType.DEFAULT)
    description: str = Field()
    owner_id: 


class ProjectOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()
    project_type: ProjectType = Field()
    description: Optional[str] = None
    owner_id: Optional[int] = None
    owner: Optional["User"] = Relationship(back_populates="projects")


class ProjectIn(SQLModel):
    name: str
    type: ProjectType
    description: Optional[str] = None
    owner_id: Optional[int] = None
