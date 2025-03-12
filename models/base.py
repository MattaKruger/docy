from typing import Optional, List
from sqlmodel import SQLModel, Field


class Base(SQLModel, table=False):
    id: Optional[int] = Field(default=None, primary_key=True)
