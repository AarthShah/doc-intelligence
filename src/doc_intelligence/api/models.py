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


class EvaluationRequest(BaseModel):
    query: str
    ground_truth: str
    contexts: List[str]


class EvaluationResponse(BaseModel):
    answer_relevance: float = Field(..., ge=0.0, le=1.0)
    faithfulness: float = Field(..., ge=0.0, le=1.0)
    hallucination_score: float = Field(..., ge=0.0, le=1.0)
    details: str = ""
