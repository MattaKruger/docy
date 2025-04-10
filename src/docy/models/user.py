from typing import TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel

from .base import Base

if TYPE_CHECKING:
    from .project import Project
    from .chat import Chat


class User(Base, SQLModel, table=True):
    __tablename__ = "users"  # type: ignore

    name: str = Field(index=True, unique=True)
    projects: List["Project"] = Relationship(
        back_populates="user", sa_relationship_kwargs=dict(lazy="selectin", cascade="all, delete-orphan")
    )
    chats: List["Chat"] = Relationship(
        back_populates="user", sa_relationship_kwargs=dict(lazy="selectin", cascade="all, delete-orphan")
    )
