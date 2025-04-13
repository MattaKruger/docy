from typing import Optional

from pydantic import BaseModel, Field

from ..models import User


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
