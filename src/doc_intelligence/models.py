"""Core data models for doc-intelligence."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid


@dataclass
class DocumentMetadata:
    """Document provenance and extraction metadata."""
    source_name: str
    format: str
    author: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    page_count: int = 1
    custom: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Document:
    """Normalized document representation."""
    text: str
    metadata: DocumentMetadata
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class Chunk:
    """A semantic chunk derived from a parent Document."""
    text: str
    chunk_index: int
    parent_doc_id: str
    token_count: int
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class QueryResult:
    """Retrieved search result with similarity score."""
    chunk: Chunk
    score: float
    retrieval_method: str = "dense"


@dataclass
class EvaluationReport:
    """Quantitative RAG evaluation metrics."""
    query: str
    answer: str
    faithfulness_score: float      # 0.0 to 1.0 (Higher = more grounded in context)
    answer_relevance_score: float  # 0.0 to 1.0 (Higher = more responsive to query)
    context_recall_score: float    # 0.0 to 1.0 (Higher = retrieved context captured ground truth)
    hallucination_score: float     # 0.0 to 1.0 (Lower = fewer unsupported statements)
    evaluated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    details: Dict[str, Any] = field(default_factory=dict)
