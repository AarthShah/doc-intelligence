import pytest
from doc_intelligence.errors import DocIntelligenceError, ParseError, RetrievalError


def test_base_doc_intelligence_error():
    err = DocIntelligenceError("Base error occurred")
    assert isinstance(err, Exception)
    assert str(err) == "Base error occurred"


def test_parse_error_inheritance():
    err = ParseError("Failed to parse document")
    assert isinstance(err, DocIntelligenceError)
    assert str(err) == "Failed to parse document"


def test_retrieval_error_inheritance():
    err = RetrievalError("Failed to retrieve documents")
    assert isinstance(err, DocIntelligenceError)
    assert str(err) == "Failed to retrieve documents"
