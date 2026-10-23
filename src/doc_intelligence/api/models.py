from typing import List
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str
    top_k: int = Field(default=5, ge=1)
    use_hybrid: bool = True


class SearchResult(BaseModel):
    doc_id: str
    content: str
    score: float


class SearchResponse(BaseModel):
    results: List[SearchResult]
