from typing import List, Optional

from pydantic import BaseModel, Field


class WebsearchResult(BaseModel):
    query: str = Field()
    result: str = Field()
    sources: List[str] = Field(default_factory=list)


class TestResult(BaseModel):
    query: str = Field()
    response: str = Field()


class SearchResult(BaseModel):
    links: Optional[str] = Field(default=None)


class Result(BaseModel):
    query: str = Field()
    response: str = Field()


class AgentContext(BaseModel):
    pass
