import pytest
from src.doc_intelligence.evaluation.faithfulness_evaluator import HallucinationDetector
from src.doc_intelligence.evaluation.mock_llm_provider import MockLLMProvider

def test_hallucination_detector_instantiation():
    """Test that HallucinationDetector can be instantiated."""
    # Instantiate with a mock LLM provider
    mock_llm = MockLLMProvider(prompt_response_map={})
    detector = HallucinationDetector(llm=mock_llm)
    assert detector is not None

def test_hallucination_detector_detect_runs():
    """Test that the detect method runs without errors with mock data."""
    mock_llm = MockLLMProvider(prompt_response_map={})
    detector = HallucinationDetector(llm=mock_llm)
    
    reference_document = "The sky is blue and the grass is green."
    generated_answer = "The sky is blue."
    context = ["The sky is blue.", "The grass is green."]
    
    try:
        is_hallucination = detector.detect(reference_document, generated_answer, context)
        assert isinstance(is_hallucination, bool)
    except Exception as e:
        pytest.fail(f"HallucinationDetector.detect raised an exception: {e}")

def test_hallucination_detector_detect_consistent():
    """
    Test that HallucinationDetector returns False for factually consistent data.
    """
    mock_llm = MockLLMProvider(prompt_response_map={})
    detector = HallucinationDetector(llm=mock_llm)
    
    reference_document = "The capital of France is Paris."
    generated_answer = "Paris is the capital of France."
    context = ["The capital of France is Paris."]
    
    is_hallucination = detector.detect(reference_document, generated_answer, context)
    
    assert not is_hallucination, "Detector should not identify factually consistent data as hallucination."

def test_hallucination_detector_detect_consistent_with_question_and_context():
    """
    Test that HallucinationDetector returns False for factually consistent data with specific question and context.
    """
    mock_llm = MockLLMProvider(prompt_response_map={})
    detector = HallucinationDetector(llm=mock_llm)
    
    question = "What is the capital of France?"
    context = ["The capital of France is Paris, known for its art and culture."]
    generated_answer = "The capital of France is Paris."
    reference_document = "The capital of France is Paris, known for its art and culture."
    
    is_hallucination = detector.detect(reference_document, generated_answer, context, question=question)
    assert not is_hallucination, "Detector should return no hallucination for consistent question, context, and answer."

def test_hallucination_detector_detect_consistent_with_question():
    """
    Test that HallucinationDetector handles question, context, and a consistent answer correctly.
    """
    mock_llm = MockLLMProvider(prompt_response_map={})
    detector = HallucinationDetector(llm=mock_llm)
    
    question = "What is the capital of France?"
    context = ["The capital of France is Paris, known for its art and culture."]
    generated_answer = "The capital of France is Paris."
    reference_document = "The capital of France is Paris, known for its art and culture."
    
    is_hallucination = detector.detect(reference_document, generated_answer, context, question=question)
    assert not is_hallucination, "Detector should return no hallucination for consistent question, context, and answer."

def test_hallucination_detector_detect_consistent_with_question_and_answer():
    """
    Test that HallucinationDetector returns False for factually consistent data with a question, context, and answer.
    """
    mock_llm = MockLLMProvider(prompt_response_map={})
    detector = HallucinationDetector(llm=mock_llm)
    
    question = "What is the capital of France?"
    context = ["The capital of France is Paris."]
    generated_answer = "Paris is the capital of France."
    reference_document = "The capital of France is Paris."

    is_hallucination = detector.detect(reference_document, generated_answer, context, question=question)
    
    assert not is_hallucination, "Detector should return no hallucination for consistent question, context, and answer."

def test_hallucination_detector_detect_hallucinates():
    """
    Test that HallucinationDetector returns True for factually inconsistent data.
    """
    # Mock LLM to always respond with "hallucination" for this specific prompt pattern
    mock_llm = MockLLMProvider(prompt_response_map={
        "Is the following answer consistent with the provided context?": "hallucination"
    })
    detector = HallucinationDetector(llm=mock_llm)
    
    reference_document = "The sun rises in the east."
    generated_answer = "The sun rises in the west."
    context = ["The sun rises in the east."]
    
    is_hallucination = detector.detect(reference_document, generated_answer, context)
    
    assert is_hallucination, "Detector should identify factually inconsistent data as hallucination."

def test_hallucination_detector_detect_unsupported_information():
    """
    Test that HallucinationDetector returns True when the answer contains information not present in the context.
    """
    # Mock LLM to always respond with "hallucination" for unsupported info
    mock_llm = MockLLMProvider(prompt_response_map={
        "Is the following answer consistent with the provided context?": "hallucination"
    })
    detector = HallucinationDetector(llm=mock_llm)
    
    reference_document = "Photosynthesis is the process used by plants to convert light into energy."
    generated_answer = "Photosynthesis converts light into energy, and plants also use it to produce chocolate."
    context = ["Photosynthesis is the process used by plants to convert light into energy."]
    
    is_hallucination = detector.detect(reference_document, generated_answer, context)
    
    assert is_hallucination, "Detector should identify unsupported information in the generated answer as a hallucination."

def test_hallucination_detector_detect_empty_inputs():
    """
    Test that HallucinationDetector handles empty strings for question, context, and answer gracefully.
    """
    mock_llm = MockLLMProvider(prompt_response_map={})
    detector = HallucinationDetector(llm=mock_llm)
    
    reference_document = ""
    generated_answer = ""
    context = []
    question = ""
    
    try:
        is_hallucination = detector.detect(reference_document, generated_answer, context, question=question)
        assert isinstance(is_hallucination, bool)
        assert not is_hallucination, "Detector should return False for empty inputs."
    except Exception as e:
        pytest.fail(f"HallucinationDetector.detect raised an exception with empty inputs: {e}")
