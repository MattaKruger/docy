from typing import List
from pydantic import BaseModel, Field


class Validate(BaseModel):
    trusted_sources: List[str] = Field(default_factory=list)
