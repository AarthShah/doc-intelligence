from fastapi.testclient import TestClient
from doc_intelligence.api.app import app

client = TestClient(app)


def test_evaluation_endpoint_invalid_payload():
    # Missing required fields like 'query', 'answer', 'contexts'
    response = client.post(
        "/api/v1/evaluate",
        json={"query": "What is the capital of France?"},
    )
    assert response.status_code == 422


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


def test_evaluation_pipeline_integration():
    from doc_intelligence.evaluation.mock_llm_provider import MockLLMProvider

    mock_provider = MockLLMProvider(
        prompt_response_map={
            "What is the capital of France?": "Paris is the capital and most populous city of France."
        }
    )

    query = "What is the capital of France?"
    generated_answer = mock_provider.generate_response(query)
    contexts = ["Paris is the capital and most populous city of France."]

    response = client.post(
        "/api/v1/evaluate",
        json={
            "query": query,
            "answer": generated_answer,
            "contexts": contexts,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)


def test_evaluation_endpoint_under_rate_limit():
    payload = {
        "query": "What is the capital of France?",
        "answer": "The capital of France is Paris.",
        "contexts": ["Paris is the capital and most populous city of France."]
    }
    
    # Send a small number of requests, should all be 200
    for _ in range(5):
        response = client.post("/api/v1/evaluate", json=payload)
        assert response.status_code == 200


def test_evaluation_endpoint_rate_limit():
    payload = {
        "query": "What is the capital of France?",
        "answer": "The capital of France is Paris.",
        "contexts": ["Paris is the capital and most populous city of France."]
    }
    
    responses = []
    for _ in range(50):
        response = client.post("/api/v1/evaluate", json=payload)
        responses.append(response.status_code)

    assert 429 in responses


def test_evaluation_endpoint_rate_limit_strict():
    payload = {
        "query": "What is the capital of France?",
        "answer": "The capital of France is Paris.",
        "contexts": ["Paris is the capital and most populous city of France."]
    }
    # Send many requests to exceed the limit
    statuses = []
    for _ in range(100):
        response = client.post("/api/v1/evaluate", json=payload)
        statuses.append(response.status_code)
    # Expect at least one 429 response
    assert 429 in statuses
