import pytest
from src.doc_intelligence.evaluation.faithfulness_evaluator import HallucinationDetector

def test_hallucination_detector_instantiation():
    """Test that HallucinationDetector can be instantiated."""
    detector = HallucinationDetector()
    assert detector is not None

def test_hallucination_detector_detect_runs():
    """Test that the detect method runs without errors with mock data."""
    detector = HallucinationDetector()
    
    # Mock data: a reference document, a generated answer, and relevant context
    reference_document = "The sky is blue and the grass is green."
    generated_answer = "The sky is blue."
    context = ["The sky is blue.", "The grass is green."]
    
    # We expect this to run without raising an exception
    try:
        is_hallucination = detector.detect(reference_document, generated_answer, context)
        # For this basic test, we don't assert the specific output, just that it runs
        # and returns a boolean.
        assert isinstance(is_hallucination, bool)
    except Exception as e:
        pytest.fail(f"HallucinationDetector.detect raised an exception: {e}")
