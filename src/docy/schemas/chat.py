from typing import Optional

from pydantic import BaseModel, Field

from ..models import Chat, Artifact, MessageType, User


class MessageIn(BaseModel):
    content: str = Field()
    message_type: MessageType = Field(default=MessageType.USER)

    chat_id: int = Field()
    artifact_id: Optional[int] = Field(default=None)


class MessageUpdate(BaseModel):
    content: Optional[str] = Field(default=None)
    message_type: Optional[MessageType] = Field(default=None)
    artifact_id: Optional[int] = Field(default=None)


class MessageOut(BaseModel):
    id: int = Field()
    content: str = Field()
    message_type: MessageType = Field()
    chat: "Chat" = Field()
    artifact: Optional["Artifact"] = Field()


class ChatIn(BaseModel):
    title: str = Field()
    user_id: int = Field()


class ChatUpdate(BaseModel):
    title: Optional[str] = Field(default=None)
    user_id: Optional[int] = Field(default=None)


class ChatOut(BaseModel):
    id: int = Field()
    title: str = Field()
    user: "User" = Field()
