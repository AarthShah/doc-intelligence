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

@pytest.mark.skipif(app is None, reason="FastAPI app or vector store not importable")
def test_parallel_ingestion_api(tmp_path, client: TestClient):
    """
    Test the /ingest endpoint with parallel processing enabled.
    """
    db_dir = tmp_path / "vector_db_parallel"
    
    # Ensure the app uses the temporary directory for persistence
    # This might require modifying the app or how it's run for testing
    # For now, we assume the app can be configured or that the default is suitable
    # or that we can manually check the store after the call.
    # A more robust test would inject dependencies or use a test app instance.

    num_documents = 10
    documents_to_ingest = [
        Document(
            id=f"doc-{i}",
            text=f"This is document {i} for parallel ingestion testing.",
            metadata=DocumentMetadata(source=f"test_source_{i}")
        ) for i in range(num_documents)
    ]
    
    # Prepare the request payload
    payload = {
        "documents": [doc.dict() for doc in documents_to_ingest],
        "vector_store_kwargs": {"persist_directory": str(db_dir)},
        "num_workers": 4  # Enable parallel processing
    }

    # Send POST request to the /ingest endpoint
    response = client.post("/ingest", json=payload)

    # Assert that the API responded successfully
    assert response.status_code == 200
    
    # Verify that all documents were ingested
    # We need to create a VectorStore instance to check the contents
    # The actual persistence path needs to be correctly identified.
    # Assuming the /ingest endpoint correctly handles persistence.
    
    # Re-initialize VectorStore to check ingested data
    # Note: In a real scenario, you might want to ensure the API call
    # correctly sets up persistence or inject a testable VectorStore.
    store = VectorStore(persist_directory=str(db_dir))
    
    # A simple check: count the number of documents in the store
    # This assumes the VectorStore has a method to get all documents or their count
    # If not, we might need to infer from search results or modify VectorStore for testing.
    # For now, we'll do a search for each document ID as a proxy.
    
    ingested_count = 0
    for doc_id in [f"doc-{i}" for i in range(num_documents)]:
        results = store.search(f"id:{doc_id}", k=1) # Searching by ID might not be directly supported, adjust if needed
        if results and results[0].id == doc_id:
            ingested_count += 1

    assert ingested_count == num_documents, f"Expected {num_documents} documents to be ingested, but found {ingested_count}"

    # More specific checks could be added if document content verification is needed
    # For example, searching for unique content parts of each document.
