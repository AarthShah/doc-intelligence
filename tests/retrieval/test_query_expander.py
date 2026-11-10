import pytest
from unittest.mock import MagicMock

from src.doc_intelligence.retrieval.query_expander import QueryExpander, HYDEQueryGenerator


@pytest.fixture
def mock_llm_provider():
    """Mocks the LLM provider."""
    mock_provider = MagicMock()
    mock_provider.generate_response.return_value = "This is a generated response."
    return mock_provider


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
    if mock_llm_provider().generate_response.return_value:
        assert len(expanded_queries) > 0
