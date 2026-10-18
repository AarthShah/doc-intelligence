import pytest

from doc_intelligence.evaluation.mock_llm_provider import MockLLMProvider
from doc_intelligence.evaluation.rag_evaluator import RAGEvaluator


def test_rag_evaluator_with_mock_llm():
    prompt_map = {
        "Evaluate the following answer against the context: ...": "entailment"
    }
    mock_llm = MockLLMProvider(prompt_response_map=prompt_map)
    evaluator = RAGEvaluator(llm_provider=mock_llm)

    contexts = ["The sky is blue."]
    answer = "The sky is blue."
    query = "What color is the sky?"

    results = evaluator.evaluate(query=query, context=contexts, answer=answer)
    assert results is not None
