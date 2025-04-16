import datetime
from typing import List, Optional

from sqlalchemy import Column, DateTime
from sqlmodel import Field, Relationship, SQLModel


def now_utc_aware():
    return datetime.datetime.now(datetime.timezone.utc)

class MessageBase(SQLModel):
    content: str = Field(index=True)
    created_at: datetime.datetime = Field(
        default_factory=now_utc_aware, sa_column=Column(DateTime(timezone=True))
    )
    chat_id: int = Field(foreign_key="chats.id", index=True)

class Message(MessageBase, table=True):
    __tablename__ = "messages"
    id: Optional[int] = Field(default=None, primary_key=True)

    chat: Optional["Chat"] = Relationship(back_populates="messages")

class MessageCreate(MessageBase):
    pass # Inherits content, chat_id

class MessageRead(MessageBase):
    id: int


class ChatBase(SQLModel):
    name: Optional[str] = Field(default=None, index=True) # Optional name for the chat
    created_at: datetime.datetime = Field(
        default_factory=now_utc_aware, sa_column=Column(DateTime(timezone=True))
    )

class Chat(ChatBase, table=True):
    __tablename__ = "chats"
    id: Optional[int] = Field(default=None, primary_key=True)

    messages: List["Message"] = Relationship(back_populates="chat")

class ChatCreate(ChatBase):
    pass # Inherits name (optional)

class ChatRead(ChatBase):
    id: int

class ChatReadWithMessages(ChatRead):
    messages: List[MessageRead] = []

Chat.update_forward_refs()
Message.update_forward_refs()
