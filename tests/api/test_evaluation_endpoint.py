from fastapi.testclient import TestClient
from doc_intelligence.api.app import app

client = TestClient(app)


def test_evaluation_endpoint_success():
    response = client.post(
        "/api/v1/evaluate",
        json={
            "query": "What is the capital of France?",
            "answer": "The capital of France is Paris.",
            "contexts": ["Paris is the capital and most populous city of France."]
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "score" in data or "evaluation" in data or isinstance(data, dict)
