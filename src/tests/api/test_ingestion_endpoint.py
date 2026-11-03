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
    Test the /documents endpoint with parallel processing enabled.
    """
    db_dir = tmp_path / "vector_db_parallel"
    num_documents = 10
    files_to_ingest = []

    # Create temporary files for ingestion
    for i in range(num_documents):
        content = f"This is document {i} for parallel ingestion testing."
        filename = f"doc_{i}.txt"
        filepath = tmp_path / filename
        with open(filepath, "w") as f:
            f.write(content)
        files_to_ingest.append(filepath)

    # Prepare the request payload
    # The endpoint now expects multipart/form-data, not JSON
    files_for_upload = [(os.path.basename(f), open(f, 'rb')) for f in files_to_ingest]
    
    # Use max_workers to explicitly test parallel processing
    payload = {
        "files": files_for_upload,
        "chunk_size": 500,
        "chunk_overlap": 50,
        "max_workers": 4
    }

    # Send POST request to the /documents endpoint
    response = client.post("/documents", files=files_for_upload, data={"chunk_size": 500, "chunk_overlap": 50, "max_workers": 4})

    # Assert that the API responded successfully
    assert response.status_code == 202  # Expecting 202 Accepted for background tasks
    response_data = response.json()
    assert response_data["message"] == "Documents received successfully and queued for parallel processing."
    assert len(response_data["received_files"]) == num_documents
    assert response_data["status"] == "processing"

    # To verify ingestion and processing, we'd typically need to check the metadata store or vector store.
    # This requires access to the underlying storage mechanisms used by the API.
    # For this test, we'll focus on the API's direct response and assume the background processing
    # will eventually succeed if no errors are raised. A more complete test would involve
    # waiting for the background task to complete and then querying the VectorStore.

    # Example of how you *might* check, assuming VectorStore is accessible and correctly configured:
    # Note: This part is highly dependent on how the FastAPI app is configured and how
    # the VectorStore is made available to background tasks.
    # If VectorStore is initialized directly in the background task, we need to ensure
    # it uses the same persistence directory.
    # For simplicity in this test, we focus on the immediate API response.

    # If you were to check the VectorStore:
    # from src.doc_intelligence.vector_store import VectorStore # Assuming it's importable in tests
    # try:
    #     # The persistence directory needs to be known or configurable for the test.
    #     # If the API uses a default or configured path, we'd use that.
    #     # For this example, let's assume it's handled or we can infer it.
    #     # This is a placeholder for actual VectorStore access.
    #     # store = VectorStore(persist_directory=SOME_EXPECTED_DIR)
    #     # assert store.count() == num_documents # If a count method exists
    #     # for i in range(num_documents):
    #     #     results = store.search(f"document {i}", k=1) # Search for content
    #     #     assert results and f"document {i}" in results[0].text
    #     pass # Placeholder
    # except Exception as e:
    #     pytest.fail(f"Could not verify VectorStore contents after ingestion: {e}")

    # Clean up temporary files
    for f_path in files_to_ingest:
        os.remove(f_path)

@pytest.mark.skipif(app is None, reason="FastAPI app or vector store not importable")
def test_single_document_ingestion_api(client: TestClient):
    """
    Test the /documents/document endpoint for single document ingestion.
    """
    filename = "single_doc.txt"
    content = "This is a single document for testing."
    
    payload = {
        "content": content,
        "filename": filename,
        "chunk_size": 500,
        "chunk_overlap": 50,
    }

    response = client.post("/documents/document", data=payload)

    assert response.status_code == 202
    response_data = response.json()
    assert response_data["message"] == "Document received successfully and queued for processing."
    assert response_data["received_files"] == [filename]
    assert response_data["status"] == "processing"

    # Similar to parallel ingestion, actual verification would involve checking
    # background task completion and the vector store.
