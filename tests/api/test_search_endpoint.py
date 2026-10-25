from fastapi.testclient import TestClient
from doc_intelligence.api.app import app, retriever

client = TestClient(app)


def test_search_endpoint_invalid_payload():
    # Invalid or missing required fields for the query endpoint
    response = client.post(
        "/query",
        json={"top_k": "invalid_type"}
    )
    assert response.status_code == 422


def test_search_endpoint():
    # Index a test document first
    ingest_response = client.post(
        "/ingest/text",
        json={
            "text": "Retrieval-augmented generation (RAG) combines search with language models.",
            "source_name": "test_source",
            "format": "plaintext",
        },
    )
    assert ingest_response.status_code == 200

    # Test query endpoint
    response = client.post(
        "/query",
        json={
            "query": "What is RAG?",
            "top_k": 3,
            "compress_context": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "What is RAG?"
    assert "results" in data
    assert isinstance(data["results"], list)


def test_search_endpoint_rate_limiting():
    # Make rapid requests to trigger rate limiting
    # We expect to hit the rate limit within 50 requests
    responses = []
    for _ in range(50):
        response = client.post(
            "/query",
            json={
                "query": "What is rate limiting?",
                "top_k": 1,
            },
        )
        responses.append(response.status_code)

    # Verify that the rate limit was triggered
    assert 429 in responses
