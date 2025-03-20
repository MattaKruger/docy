from typing import Optional
from datetime import datetime
from datetime import timezone

from sqlmodel import SQLModel, Field


class Base(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: datetime = Field(default=datetime.now(timezone.utc))
