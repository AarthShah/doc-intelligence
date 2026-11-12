import pytest
from src.doc_intelligence.evaluation.faithfulness_evaluator import FaithfulnessEvaluator

def test_faithfulness_evaluator_faithful_answer():
    """
    Test FaithfulnessEvaluator with a faithful answer.
    """
    evaluator = FaithfulnessEvaluator()
    question = "What is the capital of France?"
    answer = "The capital of France is Paris."
    context = "France is a country in Europe. Its capital is Paris."

    score = evaluator.evaluate(question=question, answer=answer, context=context)

    # Assert that the score indicates faithfulness (e.g., close to 1.0)
    # The exact score might vary slightly based on the underlying LLM,
    # but for a clearly faithful answer, it should be high.
    assert score is not None
    assert isinstance(score, float)
    assert score > 0.9  # Expect a high score for a faithful answer

def test_faithfulness_evaluator_unfaithful_answer():
    """
    Test FaithfulnessEvaluator with an unfaithful answer.
    """
    evaluator = FaithfulnessEvaluator()
    question = "What is the primary ingredient in apple pie?"
    answer = "Apple pie is mainly made of oranges."
    context = "Apple pie is a fruit pastry with a filling of sliced apples."

    score = evaluator.evaluate(question=question, answer=answer, context=context)

    # Assert that the score indicates a lack of faithfulness (e.g., close to 0.0)
    assert score is not None
    assert isinstance(score, float)
    assert score < 0.5  # Expect a low score for an unfaithful answer

def test_faithfulness_evaluator_missing_context():
    """
    Test FaithfulnessEvaluator when context is missing.
    """
    evaluator = FaithfulnessEvaluator()
    question = "What is the color of the sky?"
    answer = "The sky is blue."
    context = ""  # Empty context

    score = evaluator.evaluate(question=question, answer=answer, context=context)

    # When context is missing, the faithfulness cannot be determined.
    # The evaluator might return a neutral score or handle it specifically.
    # Assuming it might return a score indicating uncertainty or a default low score.
    assert score is not None
    assert isinstance(score, float)
    # The exact behavior here depends on the LLM's interpretation of missing context.
    # We'll assert a score that's not high, as faithfulness cannot be confirmed.
    assert score < 0.7 # Adjust threshold as needed based on observed behavior

def test_faithfulness_evaluator_edge_cases():
    """
    Test FaithfulnessEvaluator with edge cases like empty strings.
    """
    evaluator = FaithfulnessEvaluator()

    # Case 1: Empty question, answer, and context
    score1 = evaluator.evaluate(question="", answer="", context="")
    assert score1 is not None
    assert isinstance(score1, float)

    # Case 2: Empty answer
    question2 = "Test question"
    answer2 = ""
    context2 = "Some context"
    score2 = evaluator.evaluate(question=question2, answer=answer2, context=context2)
    assert score2 is not None
    assert isinstance(score2, float)

    # Case 3: Empty question
    question3 = ""
    answer3 = "Test answer"
    context3 = "Some context"
    score3 = evaluator.evaluate(question=question3, answer=answer3, context=context3)
    assert score3 is not None
    assert isinstance(score3, float)

    # The exact scores for these edge cases will depend on the LLM's behavior.
    # We assert that a float is returned and the score is not trivially perfect.
    assert score1 < 1.0
    assert score2 < 1.0
    assert score3 < 1.0
