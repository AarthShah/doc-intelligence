from unittest.mock import MagicMock, patch
import pytest

from doc_intelligence.exceptions import RetrievalError, VectorStoreError
from doc_intelligence.models import Chunk, DocumentMetadata
from doc_intelligence.retrieval.hybrid_retriever import HybridRetriever


@pytest.fixture
def sample_chunks():
    return [
        Chunk(id="1", content="First chunk content", metadata=DocumentMetadata(source="doc1")),
        Chunk(id="2", content="Second chunk content", metadata=DocumentMetadata(source="doc1")),
    ]


def test_hybrid_retriever_index_vector_store_error(sample_chunks):
    retriever = HybridRetriever()
    retriever.vector_store = MagicMock()
    retriever.vector_store.add_chunks.side_effect = VectorStoreError("Vector store down")

    with pytest.raises(RetrievalError) as exc_info:
        retriever.index(sample_chunks)
    assert "Failed to index chunks" in str(exc_info.value)


def test_hybrid_retriever_index_unexpected_error(sample_chunks):
    retriever = HybridRetriever()
    retriever.vector_store = MagicMock()
    retriever.vector_store.add_chunks.side_effect = RuntimeError("Unexpected error")

    with pytest.raises(RetrievalError) as exc_info:
        retriever.index(sample_chunks)
    assert "Failed to index chunks" in str(exc_info.value)


def test_hybrid_retriever_search_vector_store_error():
    retriever = HybridRetriever()
    retriever.vector_store = MagicMock()
    retriever.vector_store.search.side_effect = VectorStoreError("Vector search failed")

    with pytest.raises(RetrievalError) as exc_info:
        retriever.search("test query")
    assert "Vector store search failed" in str(exc_info.value)


def test_hybrid_retriever_search_unexpected_dense_error():
    retriever = HybridRetriever()
    retriever.vector_store = MagicMock()
    retriever.vector_store.search.side_effect = RuntimeError("Unexpected dense error")

    with pytest.raises(RetrievalError) as exc_info:
        retriever.search("test query")
    assert "Unexpected error during dense search" in str(exc_info.value)


def test_hybrid_retriever_search_bm25_error():
    retriever = HybridRetriever()
    retriever.vector_store = MagicMock()
    retriever.vector_store.search.return_value = []
    retriever.bm25 = MagicMock()
    retriever.bm25.search.side_effect = Exception("BM25 index corrupted")

    with pytest.raises(RetrievalError) as exc_info:
        retriever.search("test query")
    assert "BM25 search failed" in str(exc_info.value)
