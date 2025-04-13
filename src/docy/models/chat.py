from typing import List, Optional

from sqlmodel import Field, Relationship

from .base import Base
from .message import Message
from .user import User


class Chat(Base, table=True):
    __tablename__ = "chats"  # type: ignore

    title: str = Field(index=True)
    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="chats", sa_relationship_kwargs=dict(lazy="selectin"))
    messages: Optional[List["Message"]] = Relationship(
        back_populates="chat", sa_relationship_kwargs=dict(lazy="selectin")
    )
