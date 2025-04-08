from typing import List, Optional

from pydantic import BaseModel, Field

from ..models import Project


class UserIn(BaseModel):
    name: str = Field()


class UserOut(BaseModel):
    id: int = Field()
    name: str = Field()


class UserUpdate(BaseModel):
    name: Optional[str] = Field()


class UserProjects(BaseModel):
    id: int
    name: str
    projects: Optional[List["Project"]]
