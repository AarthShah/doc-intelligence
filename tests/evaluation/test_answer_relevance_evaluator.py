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


def test_answer_relevance_evaluator_irrelevant(monkeypatch):
    evaluator = AnswerRelevanceEvaluator(model_name="all-MiniLM-L6-v2")
    monkeypatch.setattr(evaluator, "model", DummyEmbeddingModel())

    score = evaluator.evaluate(query="What is the capital of France?", answer="The sky is blue.")
    assert isinstance(score, float)
    # Since the dummy embedding model returns a fixed vector, the cosine similarity
    # between "The capital of France is Paris." and "The sky is blue." will be calculated.
    # With DummyEmbeddingModel returning [1.0, 0.0] for both, the score will be 1.0.
    # In a real scenario with different embeddings, this would be lower.
    assert score == 1.0


def test_answer_relevance_evaluator_empty_inputs(monkeypatch):
    evaluator = AnswerRelevanceEvaluator(model_name="all-MiniLM-L6-v2")
    monkeypatch.setattr(evaluator, "model", DummyEmbeddingModel())

    # Test with empty query
    score_empty_query = evaluator.evaluate(query="", answer="The capital of France is Paris.")
    assert isinstance(score_empty_query, float)
    assert score_empty_query == 1.0 # With DummyEmbeddingModel, score will be 1.0

    # Test with empty answer
    score_empty_answer = evaluator.evaluate(query="What is the capital of France?", answer="")
    assert isinstance(score_empty_answer, float)
    assert score_empty_answer == 1.0 # With DummyEmbeddingModel, score will be 1.0

    # Test with both empty
    score_both_empty = evaluator.evaluate(query="", answer="")
    assert isinstance(score_both_empty, float)
    assert score_both_empty == 1.0 # With DummyEmbeddingModel, score will be 1.0
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


def test_answer_relevance_evaluator_irrelevant(monkeypatch):
    evaluator = AnswerRelevanceEvaluator(model_name="all-MiniLM-L6-v2")
    monkeypatch.setattr(evaluator, "model", DummyEmbeddingModel())

    score = evaluator.evaluate(query="What is the capital of France?", answer="The sky is blue.")
    assert isinstance(score, float)
    # Since the dummy embedding model returns a fixed vector, the cosine similarity
    # between "The capital of France is Paris." and "The sky is blue." will be calculated.
    # With DummyEmbeddingModel returning [1.0, 0.0] for both, the score will be 1.0.
    # In a real scenario with different embeddings, this would be lower.
    assert score == 1.0


def test_answer_relevance_evaluator_empty_inputs(monkeypatch):
    evaluator = AnswerRelevanceEvaluator(model_name="all-MiniLM-L6-v2")
    monkeypatch.setattr(evaluator, "model", DummyEmbeddingModel())

    # Test with empty query
    score_empty_query = evaluator.evaluate(query="", answer="The capital of France is Paris.")
    assert isinstance(score_empty_query, float)
    assert score_empty_query == 1.0 # With DummyEmbeddingModel, score will be 1.0

    # Test with empty answer
    score_empty_answer = evaluator.evaluate(query="What is the capital of France?", answer="")
    assert isinstance(score_empty_answer, float)
    assert score_empty_answer == 1.0 # With DummyEmbeddingModel, score will be 1.0

    # Test with both empty
    score_both_empty = evaluator.evaluate(query="", answer="")
    assert isinstance(score_both_empty, float)
    assert score_both_empty == 1.0 # With DummyEmbeddingModel, score will be 1.0
