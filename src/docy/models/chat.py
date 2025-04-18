import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel


from .user import User


def now_utc_aware():
    return datetime.datetime.now(datetime.timezone.utc)


class MessageBase(SQLModel):
    content: str = Field(index=True)
    created_at: datetime.datetime = Field(
        default_factory=now_utc_aware, sa_column=Column(DateTime(timezone=True))
    )
    chat_id: int = Field(foreign_key="chats.id", index=True)


class Message(MessageBase, table=True):
    __tablename__ = "messages" # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)

    chat: Optional["Chat"] = Relationship(back_populates="messages")


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int


class ChatBase(SQLModel):
    name: str = Field(index=True)
    created_at: datetime.datetime = Field(
        default_factory=now_utc_aware, sa_column=Column(DateTime(timezone=True))
    )


class Chat(ChatBase, table=True):
    __tablename__ = "chats" # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)

    messages: List["Message"] = Relationship(back_populates="chat")
    user_id: int = Field(foreign_key="users.id")
    user: "User" = Relationship(back_populates="chats")


class ChatCreate(ChatBase):
    pass


class ChatRead(ChatBase):
    id: int
    user: "User"


class ChatReadWithMessages(ChatRead):
    messages: List[MessageRead] = []


Chat.model_rebuild()
ChatRead.model_rebuild()
Message.model_rebuild()
