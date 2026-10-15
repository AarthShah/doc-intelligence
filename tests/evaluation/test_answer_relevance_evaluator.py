import pytest
from doc_intelligence.evaluation.answer_relevance_evaluator import AnswerRelevanceEvaluator


class DummyEmbeddingModel:
    def encode(self, text: str, convert_to_tensor: bool = False):
        return [1.0, 0.0]


def test_answer_relevance_evaluator_init():
    evaluator = AnswerRelevanceEvaluator(model_name="all-MiniLM-L6-v2")
    assert evaluator.model is not None


def test_answer_relevance_evaluator_evaluate(monkeypatch):
    evaluator = AnswerRelevanceEvaluator(model_name="all-MiniLM-L6-v2")
    monkeypatch.setattr(evaluator, "model", DummyEmbeddingModel())

    score = evaluator.evaluate(query="What is the capital of France?", answer="The capital of France is Paris.")
    assert isinstance(score, float)
    assert score == 1.0
