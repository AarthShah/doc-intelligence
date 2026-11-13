import pytest
from fastapi.testclient import TestClient
from doc_intelligence.api.app import app

def test_limiter_attached():
    assert hasattr(app.state, "limiter")
    from slowapi import Limiter
    assert isinstance(app.state.limiter, Limiter)
