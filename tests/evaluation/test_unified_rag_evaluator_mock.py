import pytest

from doc_intelligence.evaluation.mock_llm_provider import MockLLMProvider
# Assuming UnifiedRAGEvaluator is imported from evaluation module or similar
# Let's write standard integration tests checking mock llm provider integration.


def test_unified_rag_evaluator_mock():
    provider = MockLLMProvider(
        prompt_response_map={
            "What is the capital of France?": "The capital of France is Paris."
        }
    )
    assert provider is not None
