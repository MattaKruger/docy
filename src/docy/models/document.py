import os
from typing import List, Optional

import numpy as np
from pgvector.sqlalchemy import Vector
from sentence_transformers import SentenceTransformer
from sqlmodel import Column, Field, SQLModel

MODEL_NAME = "all-MiniLM-L6-v2"
VECTOR_DIMENSIONS = 384


class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(index=True)

    embedding: Optional[List[float]] = Field(default=None, sa_column=Column(Vector(VECTOR_DIMENSIONS)))
