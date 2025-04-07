from typing import List, Optional

from ..models import Project
from pydantic import BaseModel, Field


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
