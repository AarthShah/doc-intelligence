import os
import tempfile
import pytest
from fastapi.testclient import TestClient

try:
    from src.doc_intelligence.api.app import app
    from src.doc_intelligence.vector_store import VectorStore
    from src.doc_intelligence.models import Document, DocumentMetadata
except ImportError:
    app = None


@pytest.mark.skipif(app is None, reason="FastAPI app or vector store not importable")
def test_vector_store_persistence_and_retrieval(tmp_path):
    """
    Test that data ingested and persisted in VectorStore is retrievable
    after simulating an application/store restart.
    """
    db_dir = tmp_path / "vector_db"
    
    # Initialize first vector store instance and add documents
    store1 = VectorStore(persist_directory=str(db_dir))
    doc = Document(
        id="doc-1",
        text="Persistent vector store test content for document intelligence.",
        metadata=DocumentMetadata(source="test_source")
    )
    store1.add([doc])
    store1.persist()

    # Simulate restart by creating a new VectorStore instance pointing to the same directory
    store2 = VectorStore(persist_directory=str(db_dir))
    
    results = store2.search("document intelligence", k=1)
    assert len(results) > 0
    assert results[0].id == "doc-1"
    assert "Persistent vector store" in results[0].text
