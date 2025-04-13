from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Column, Field, Relationship, Text

from .base import Base
from .task import Task

if TYPE_CHECKING:
    from .artifact import Artifact
    from .chat import Chat


# Rethink Mesagetype, Not sure if we want this in message or even at all.
class MessageType(str, Enum):
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"
    DEFAULT = "default"


class Message(Base, table=True):
    __table__name = "messages"  # type: ignore

    content: str = Field(sa_column=Column(Text))
    message_type: MessageType = Field(default=MessageType.DEFAULT.value)

    chat_id: Optional[int] = Field(default=None, foreign_key="chats.id")
    chat: Optional["Chat"] = Relationship(back_populates="messages", sa_relationship_kwargs=dict(lazy="selectin"))
    artifact_id: Optional[int] = Field(default=None, foreign_key="artifacts.id")
    artifact: Optional["Artifact"] = Relationship(
        back_populates="message", sa_relationship_kwargs=dict(lazy="selectin")
    )
    task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")
    task: Optional[Task] = Relationship(back_populates="messages", sa_relationship_kwargs=dict(lazy="selectin"))
