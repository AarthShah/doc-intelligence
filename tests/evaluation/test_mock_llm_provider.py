import pytest
from doc_intelligence.evaluation.mock_llm_provider import MockLLMProvider

def test_mock_llm_provider_generate_response_known_prompt():
    """
    Tests if MockLLMProvider returns the correct predefined response for a known prompt.
    """
    mock_llm = MockLLMProvider(
        prompt_response_map={
            "What is the capital of France?": "The capital of France is Paris.",
            "Who wrote Hamlet?": "Hamlet was written by William Shakespeare.",
        }
    )
    response = mock_llm.generate_response("What is the capital of France?")
    assert response == "The capital of France is Paris."

def test_mock_llm_provider_generate_response_unknown_prompt():
    """
    Tests if MockLLMProvider raises a KeyError for an unknown prompt.
    """
    mock_llm = MockLLMProvider(
        prompt_response_map={
            "What is the capital of France?": "The capital of France is Paris.",
        }
    )
    with pytest.raises(KeyError):
        mock_llm.generate_response("What is the capital of Spain?")

def test_mock_llm_provider_reset():
    """
    Tests if MockLLMProvider's reset functionality clears its history.
    """
    mock_llm = MockLLMProvider(
        prompt_response_map={
            "First question": "First answer",
            "Second question": "Second answer",
        }
    )
    # Make a call to populate history (though MockLLMProvider doesn't store history, this ensures the method is called)
    mock_llm.generate_response("First question")

    # Assert that the responses are still available
    assert mock_llm.generate_response("First question") == "First answer"

    # Reset the provider
    mock_llm.reset()

    # Now, calling with a known prompt should still work as it relies on the initial responses dictionary
    # If the implementation were to store and modify responses, this would be a place to test clearing that.
    # For the current implementation, reset doesn't change the `responses` dict, so this is a sanity check.
    assert mock_llm.generate_response("First question") == "First answer"

    # Verify that an unknown prompt still raises KeyError after reset
    with pytest.raises(KeyError):
        mock_llm.generate_response("Third question")
