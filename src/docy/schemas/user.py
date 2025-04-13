from typing import List, Optional

from pydantic import BaseModel, Field

from ..models import Chat, Project


class UserIn(BaseModel):
    name: str = Field()


class UserOut(BaseModel):
    id: int = Field()
    name: str = Field()
    projects: Optional[List["Project"]]
    chats: Optional[List["Chat"]]


class UserUpdate(BaseModel):
    name: Optional[str] = Field()


class UserProjects(BaseModel):
    id: int
    name: str
    projects: Optional[List["Project"]]
