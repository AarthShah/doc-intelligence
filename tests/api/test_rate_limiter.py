import pytest
from fastapi import HTTPException
from starlette.requests import Request
from starlette.datastructures import Headers
from starlette.types import Scope

from src.doc_intelligence.api.rate_limiter import RateLimiter

def _make_request(client_host: str) -> Request:
    scope: Scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "headers": Headers({}).raw,
        "client": (client_host, 12345),
    }
    return Request(scope)

@pytest.mark.asyncio
async def test_rate_limiter_allows_first_request():
    limiter = RateLimiter(requests_per_unit=2, unit_seconds=10)
    request = _make_request("1.2.3.4")
    await limiter(request)  # should not raise

@pytest.mark.asyncio
async def test_rate_limiter_blocks_excess_requests():
    limiter = RateLimiter(requests_per_unit=1, unit_seconds=10)
    request = _make_request("5.6.7.8")
    await limiter(request)  # first request ok
    with pytest.raises(HTTPException) as exc:
        await limiter(request)  # second request exceeds limit
    assert exc.value.status_code == 429
