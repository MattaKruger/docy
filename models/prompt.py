from typing import Optional
from datetime import datetime

from rich.color import Color
from sqlmodel import SQLModel, Field, Relationship, Column
from sqlalchemy import Text


from .base import Base


class Prompt(Base, table=True):
    name: str = Field(index=True, unique=True, description="Unique name for the prompt")
    content: str = Field(sa_column=Column(Text), description="The full text content of the system prompt.")


class PromptIn(SQLModel):
    """
    Schema for creating a new Prompt.
    """
    name: str = Field(description="Unique name for the prompt")
    content: str = Field(description="The full text content of the system prompt")


class PromptOut(SQLModel):
    """
    Schema for reading/returning Prompt data. Includes generated fields.
    """
    id: int
    name: str
    content: str
    created_at: datetime
    updated_at: datetime


class PromptUpdate(SQLModel):
    """
    Schema for updating an existing Prompt. All fields are optional.
    """
    name: Optional[str] = Field(default=None, description="New unique name for the prompt")
    content: Optional[str] = Field(default=None, description="New full text content for the prompt")
