from typing import Optional

from sqlmodel import Field, SQLModel


class Base(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True, index=True, nullable=False)
