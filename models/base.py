from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, event
from sqlmodel import Field, SQLModel


class Base(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column=Column(index=True))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


@event.listens_for(Base, "before_update")
def before_update(mapper, connection, target):
    target.updated_at = datetime.now(timezone.utc)
