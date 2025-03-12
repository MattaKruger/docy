from typing import TYPE_CHECKING

from enum import Enum
from typing import Optional
from sqlmodel import SQLModel, Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User


class ProjectType(str, Enum):
    DEFAULT = "default"
    CODE = "code"


class Project(Base, table=True):
    name: str = Field()
    project_type: ProjectType = Field(default=ProjectType.DEFAULT)
    description: str = Field()
    framework: str = Field()
    owner_id: Optional[int] = Field(default=None, foreign_key="users.id")
    owner: Optional["User"] = Relationship(back_populates="projects")

    __tablename__ = "projects" # type:ignore


class ProjectOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()
    project_type: ProjectType = Field()
    description: Optional[str] = None
    owner_id: Optional[int] = None


class ProjectIn(SQLModel, table=False):
    name: str = Field()
    project_type: ProjectType = Field()
    description: Optional[str] = None
    framework: str = Field()
    owner_id: Optional[int] = None


class ProjectUpdate(SQLModel, table=False):
    name: Optional[str] = None
    type: Optional[ProjectType] = None
    description: Optional[str] = None
    owner_id: Optional[int] = None
