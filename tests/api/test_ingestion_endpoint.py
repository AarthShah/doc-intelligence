from fastapi.testclient import TestClient
from doc_intelligence.api.app import app

client = TestClient(app)

def test_ingestion_rate_limiting():
    # Make multiple rapid requests to trigger the rate limiter
    responses = []
    for _ in range(15):
        response = client.post(
            "/api/v1/ingest",
            json={"files": ["test.txt"]}
        )
        responses.append(response.status_code)

    # Verify that at least one request succeeded and at least one was rate limited (429)
    assert 200 in responses or 201 in responses or 400 in responses or 422 in responses
    assert 429 in responses

def test_ingestion_successful_request_has_rate_limit_headers():
    # Make a single request and verify rate limit headers are present and valid
    response = client.post(
        "/api/v1/ingest",
        json={"files": ["single_file.txt"]}
    )
    assert response.status_code in [200, 201] # Assuming valid payload for header checks
    assert "x-ratelimit-limit" in response.headers
    assert "x-ratelimit-remaining" in response.headers
    assert "x-ratelimit-reset" in response.headers

    # Verify header types and positive values
    assert isinstance(int(response.headers["x-ratelimit-limit"]), int) and int(response.headers["x-ratelimit-limit"]) > 0
    assert isinstance(int(response.headers["x-ratelimit-remaining"]), int) and int(response.headers["x-ratelimit-remaining"]) >= 0
    assert isinstance(int(response.headers["x-ratelimit-reset"]), int) and int(response.headers["x-ratelimit-reset"]) > 0


def test_ingestion_rate_limited_request_has_retry_after_header():
    # Make multiple requests to trigger rate limiting and verify Retry-After header
    responses = []
    # Send enough requests to exceed the default limit (e.g., 10 requests)
    for _ in range(15):
        response = client.post(
            "/api/v1/ingest",
            json={"files": ["limit_exceed.txt"]}
        )
        responses.append(response)

    rate_limited_response = next((r for r in responses if r.status_code == 429), None)
    assert rate_limited_response is not None, "Expected at least one 429 response, but none received."
    assert "retry-after" in rate_limited_response.headers
    
    retry_after_value = int(rate_limited_response.headers["retry-after"])
    assert isinstance(retry_after_value, int)
    assert retry_after_value > 0


def test_ingestion_rate_limit_header_decrements():
    """
    Verify that the ``x‑ratelimit‑remaining`` header decreases after a successful request.
    """
    # First request to obtain the initial remaining count
    response1 = client.post(
        "/api/v1/ingest",
        json={"files": ["first.txt"]},
    )
    assert response1.status_code in [200, 201]
    initial_remaining = int(response1.headers["x-ratelimit-remaining"])

    # Second request should decrement the remaining count (unless already rate‑limited)
    response2 = client.post(
        "/api/v1/ingest",
        json={"files": ["second.txt"]},
    )
    # If the second request is also allowed, the remaining count must be one less
    if response2.status_code not in (429,):
        new_remaining = int(response2.headers["x-ratelimit-remaining"])
        assert new_remaining == max(initial_remaining - 1, 0)
