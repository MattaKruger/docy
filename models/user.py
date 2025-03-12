from sqlmodel import SQLModel, Field, Relationship
from .base import Base
from .project import Project

class User(Base, SQLModel, table=True):
    user: str = Field(index=True)
    projects: list["Project"] = Relationship(back_populates="owner")
