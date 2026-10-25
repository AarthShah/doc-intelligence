import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient

from doc_intelligence.api.routers.evaluation import router, EvaluationRequest

app = FastAPI()
app.include_router(router)

client = TestClient(app)


def make_request():
    payload = {
        "query": "What is the capital of France?",
        "response": "Paris is the capital of France.",
        "retrieved_contexts": ["Paris is a city in France."],
    }
    return client.post("/api/v1/evaluation", json=payload)


def test_rate_limiter_allows_up_to_limit():
    # The limit is set to 10 requests per 60 seconds.
    for _ in range(10):
        response = make_request()
        assert response.status_code == status.HTTP_200_OK

def test_rate_limiter_blocks_excess_requests():
    # Exhaust the limit first
    for _ in range(10):
        client.post("/api/v1/evaluation", json={
            "query": "q",
            "response": "r",
            "retrieved_contexts": []
        })
    # The 11th request should be rate limited
    response = client.post("/api/v1/evaluation", json={
        "query": "q",
        "response": "r",
        "retrieved_contexts": []
    })
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS
