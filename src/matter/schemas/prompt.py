from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class PromptIn(BaseModel):
    """
    Schema for creating a new Prompt.
    """

    name: str = Field(description="Unique name for the prompt")
    content: str = Field(description="The full text content of the system prompt")


class PromptOut(BaseModel):
    """
    Schema for reading/returning Prompt data. Includes generated fields.
    """

    id: int
    name: str
    content: str
    created_at: datetime
    updated_at: datetime


class PromptUpdate(BaseModel):
    """
    Schema for updating an existing Prompt. All fields are optional.
    """

    name: Optional[str] = Field(default=None, description="New unique name for the prompt")
    content: Optional[str] = Field(default=None, description="New full text content for the prompt")
