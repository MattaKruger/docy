from typing import Optional
from datetime import datetime
from sqlmodel import SQLModel, Field


class Base(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default=datetime.utcnow())
    updated_at: datetime = Field(default=datetime.utcnow())
