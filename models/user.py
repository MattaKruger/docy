from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

from .base import Base
from .project import Project


class User(Base, SQLModel, table=True):
    name: str = Field(index=True, unique=True)
    projects: List["Project"] = Relationship(back_populates="owner")

    __tablename__ = "users"  # type: ignore


class UserIn(SQLModel, table=False):
    name: str = Field()


class UserOut(SQLModel, table=False):
    id: int = Field()
    name: str = Field()


class UserUpdate(SQLModel, table=False):
    name: Optional[str] = Field()


class UserProjects(SQLModel, table=False):
    id: int
    name: str
    projects: Optional[List["Project"]] = None
