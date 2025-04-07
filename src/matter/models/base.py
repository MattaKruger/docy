from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


def now_tz():
    return datetime.now(timezone.utc)


class Base(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True, index=True, nullable=False)

    # created_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    # updated_at: datetime = Field(
    #     sa_column=Column(
    #         DateTime(timezone=True),
    #         nullable=False,
    #         server_default=func.now(),
    #         onupdate=func.now()
    #     ),
    # )
