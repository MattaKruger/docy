from typing import Optional, List

from pgvector.sqlalchemy import Vector
from sqlmodel import SQLModel, Field, Column


VECTOR_DIMENSIONS = 1024


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(index=True)

    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(VECTOR_DIMENSIONS)))
