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

def test_hallucination_detector_detect_consistent():
    """
    Test that HallucinationDetector returns False for factually consistent data.
    """
    detector = HallucinationDetector()
    
    # Factually consistent data
    reference_document = "The capital of France is Paris."
    generated_answer = "Paris is the capital of France."
    context = ["The capital of France is Paris."]
    
    is_hallucination = detector.detect(reference_document, generated_answer, context)
    
    assert not is_hallucination, "Detector should not identify factually consistent data as hallucination."

def test_hallucination_detector_detect_consistent_with_question_and_context():
    """
    Test that HallucinationDetector returns False for factually consistent data with specific question and context.
    """
    detector = HallucinationDetector()
    
    question = "What is the capital of France?"
    context = ["The capital of France is Paris, known for its art and culture."]
    generated_answer = "The capital of France is Paris."
    reference_document = "The capital of France is Paris, known for its art and culture."
    
    # Depending on signature support or kwargs in detectors, test standard detect call
    is_hallucination = detector.detect(reference_document, generated_answer, context)
    assert not is_hallucination, "Detector should return no hallucination for consistent question, context, and answer."

def test_hallucination_detector_detect_consistent_with_question():
    """
    Test that HallucinationDetector handles question, context, and a consistent answer correctly.
    """
    detector = HallucinationDetector()
    
    question = "What is the capital of France?"
    context = ["The capital of France is Paris, known for its art and culture."]
    generated_answer = "The capital of France is Paris."
    reference_document = "The capital of France is Paris, known for its art and culture."
    
    # Depending on signature support or kwargs in detectors, test standard detect call
    is_hallucination = detector.detect(reference_document, generated_answer, context)
    assert not is_hallucination, "Detector should return no hallucination for consistent question, context, and answer."

def test_hallucination_detector_detect_consistent_with_question_and_answer():
    """
    Test that HallucinationDetector returns False for factually consistent data with a question, context, and answer.
    """
    detector = HallucinationDetector()
    
    question = "What is the capital of France?"
    context = ["The capital of France is Paris."]
    generated_answer = "Paris is the capital of France."
    reference_document = "The capital of France is Paris."

    is_hallucination = detector.detect(reference_document, generated_answer, context)
    
    assert not is_hallucination, "Detector should return no hallucination for consistent question, context, and answer."

def test_hallucination_detector_detect_hallucinates():
    """
    Test that HallucinationDetector returns True for factually inconsistent data.
    """
    detector = HallucinationDetector()
    
    # Factually inconsistent data
    reference_document = "The sun rises in the east."
    generated_answer = "The sun rises in the west."
    context = ["The sun rises in the east."]
    
    is_hallucination = detector.detect(reference_document, generated_answer, context)
    
    assert is_hallucination, "Detector should identify factually inconsistent data as hallucination."
