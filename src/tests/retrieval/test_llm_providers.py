import pytest
from unittest.mock import patch, MagicMock
from doc_intelligence.models import LLMProvider
from doc_intelligence.retrieval.llm_providers import HuggingFaceInferenceAPIProvider


class MockLLMProvider(LLMProvider):
    """A shared mock LLM provider for testing retrieval components."""

    def __init__(self, response: str = "Mocked response text"):
        self.response = response
        self.last_prompt = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.response


def test_huggingface_inference_api_provider_success():
    provider = HuggingFaceInferenceAPIProvider(
        model_name="test-model", api_key="fake-key"
    )

    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = [{"generated_text": "Mocked response text"}]

    with patch("requests.post", return_value=mock_response) as mock_post:
        response = provider.generate("Test prompt")

        assert response == "Mocked response text"
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert "test-model" in kwargs["url"] or "test-model" in args[0]
        assert kwargs["headers"]["Authorization"] == "Bearer fake-key"
        assert kwargs["json"]["inputs"] == "Test prompt"


def test_huggingface_inference_api_provider_error():
    provider = HuggingFaceInferenceAPIProvider(
        model_name="test-model", api_key="fake-key"
    )

    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"

    with patch("requests.post", return_value=mock_response):
        with pytest.raises(Exception):
            provider.generate("Test prompt")
