from typing import List, TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

from .base import Base

if TYPE_CHECKING:
    from .project import Project


class User(Base, SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    name: str = Field(index=True, unique=True)
    projects: List["Project"] = Relationship(back_populates="user")
