from enum import Enum
from typing import TYPE_CHECKING, List

from sqlalchemy import Text
from sqlmodel import Column, Field, Relationship

from .base import Base

if TYPE_CHECKING:
    from .agent import Agent


class PromptType(str, Enum):
    DEFAULT = "default"
    CODING = "coding"


class Prompt(Base, table=True):
    __tablename__ = "prompts"  # type: ignore

    name: str = Field(index=True, unique=True, description="Unique name for the prompt")
    content: str = Field(sa_column=Column(Text), description="The full text content of the system prompt.")

    agents: List["Agent"] = Relationship(back_populates="system_prompt", sa_relationship_kwargs=dict(lazy="selectin"))
