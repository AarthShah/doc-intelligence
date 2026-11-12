"""Exceptions module backwards-compatibility alias for errors.py."""

from doc_intelligence.errors import (
    DocIntelligenceError,
    ParsingError,
    UnsupportedDocumentTypeError,
    RetrievalError,
    VectorStoreError,
)

# Backwards compatibility alias
DocumentIntelligenceError = DocIntelligenceError

__all__ = [
    "DocIntelligenceError",
    "DocumentIntelligenceError",
    "ParsingError",
    "UnsupportedDocumentTypeError",
    "RetrievalError",
    "VectorStoreError",
]

