from typing import List, Optional
from pydantic import BaseModel, Field
from src.doc_intelligence.models import Document

class SearchRequest(BaseModel):
    """Request model for the search endpoint."""
    query: str = Field(..., min_length=1, description="The user query.")
    k: int = Field(default=5, ge=1, description="Number of results to return.")
    rerank_top_n: int = Field(default=10, ge=1, description="Number of results to rerank.")
    use_hybrid: bool = Field(default=True, description="Whether to use hybrid search.")

class SearchResult(BaseModel):
    """Represents a single search result."""
    document: Document
    score: float

class SearchResponse(BaseModel):
    """Response model for the search endpoint."""
    results: List[SearchResult]

class MetricScore(BaseModel):
    """Score for an individual evaluation metric."""
    metric_name: str
    score: float
    details: Optional[str] = None

class EvaluationRequest(BaseModel):
    """Request model for RAG evaluation."""
    query: str = Field(..., min_length=1, description="The user query.")
    response: str = Field(..., min_length=1, description="The generated RAG response.")
    retrieved_contexts: List[str] = Field(default_factory=list, description="The contexts retrieved for the query.")
    reference: Optional[str] = Field(None, description="Optional ground truth reference answer.")

class EvaluationResponse(BaseModel):
    """Response model for RAG evaluation."""
    status: str = "success"
    scores: List[MetricScore] = Field(default_factory=list)
    summary: Optional[str] = None

class DocumentIngestRequest(BaseModel):
    content: str = Field(..., min_length=1)
    metadata: dict = Field(default_factory=dict)
