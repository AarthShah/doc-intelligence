import pytest
from unittest.mock import MagicMock

from src.doc_intelligence.retrieval.query_expander import QueryExpander, HYDEQueryGenerator


class MockLLMProvider:
    """
    A mock LLM provider that returns predefined expanded queries.
    """
    def __init__(self, prompt_response_map: dict):
        self.prompt_response_map = prompt_response_map

    def generate_response(self, prompt: str, **kwargs) -> str:
        return self.prompt_response_map.get(prompt, "default expanded query")


@pytest.fixture
def mock_llm_provider():
    """Mocks the LLM provider with predefined responses."""
    mock_responses = {
        "What is the capital of France?": "What is the major city of France? Tell me about Paris.",
        "Who was the first president of the United States?": "Who was the initial leader of America? Information on George Washington.",
    }
    return MockLLMProvider(prompt_response_map=mock_responses)


@pytest.fixture
def query_expander(mock_llm_provider):
    """Provides a QueryExpander instance with a mocked LLM provider."""
    hyde_generator = HYDEQueryGenerator(llm_provider=mock_llm_provider)
    return QueryExpander(hyde_generator=hyde_generator)


def test_query_expander_expand_query(query_expander):
    """Tests that QueryExpander.expand_query returns a list of strings."""
    query = "What is the capital of France?"
    expanded_queries = query_expander.expand_query(query)

    assert isinstance(expanded_queries, list)
    assert all(isinstance(q, str) for q in expanded_queries)
    # Add more specific assertions based on expected output if needed
    # For now, we just check the type and that it's not empty if the mock provides a response.
    assert len(expanded_queries) > 0
    assert "What is the major city of France?" in expanded_queries
    assert "Tell me about Paris." in expanded_queries


def test_query_expander_expand_query_empty_input(query_expander):
    """Tests that QueryExpander.expand_query returns an empty list for an empty query."""
    query = ""
    expanded_queries = query_expander.expand_query(query)

    assert expanded_queries == []
