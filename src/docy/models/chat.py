from enum import Enum
from typing import List, Optional

from sqlmodel import Column, Field, Relationship, Text

from .artifact import Artifact
from .base import Base
from .user import User


class MessageType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Message(Base, table=True):
    __table__name = "messages"  # type: ignore

    content: str = Field(sa_column=Column(Text))
    message_type: MessageType = Field(default=MessageType.USER.value)

    chat_id: int = Field(foreign_key="chats.id")
    chat: "Chat" = Relationship(back_populates="messages", sa_relationship_kwargs=dict(lazy="selectin"))
    artifact_id: Optional[int] = Field(default=None, foreign_key="artifacts.id")
    artifact: Optional["Artifact"] = Relationship(
        back_populates="message", sa_relationship_kwargs=dict(lazy="selectin")
    )


class Chat(Base, table=True):
    __tablename__ = "chats"  # type: ignore

    title: str = Field(index=True)
    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="chats", sa_relationship_kwargs=dict(lazy="selectin"))
    messages: Optional[List["Message"]] = Relationship(
        back_populates="chat", sa_relationship_kwargs=dict(lazy="selectin")
    )
