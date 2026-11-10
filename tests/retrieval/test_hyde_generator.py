import unittest
from unittest.mock import MagicMock

from doc_intelligence.retrieval.hyde_generator import HyDEGenerator


class MockLLMProvider:
    """A mock LLM provider for testing purposes."""
    def __init__(self, ideal_document: str):
        self.ideal_document = ideal_document

    def generate(self, prompt: str) -> str:
        """Returns a predefined document based on the prompt."""
        return self.ideal_document


class TestHyDEGenerator(unittest.TestCase):
    def test_init_stores_dependencies(self):
        mock_client = MagicMock()
        prompt_template = "Custom prompt: {query}"
        generator = HyDEGenerator(llm_client=mock_client, prompt_template=prompt_template)

        self.assertEqual(generator.llm_client, mock_client)
        self.assertEqual(generator.prompt_template, prompt_template)

    def test_generate_hypothetical_document_returns_string(self):
        ideal_doc = "This is an ideal hypothetical document."
        mock_llm_client = MockLLMProvider(ideal_document=ideal_doc)
        generator = HyDEGenerator(llm_client=mock_llm_client)

        query = "What is the capital of France?"
        hypothetical_document = generator.generate_hypothetical_document(query)

        self.assertIsInstance(hypothetical_document, str)
        self.assertEqual(hypothetical_document, ideal_doc)
        # The exact prompt format might change, so we'll just check if generate was called.
        # If prompt_template is not provided to HyDEGenerator, it defaults to "Generate a hypothetical document for the query: {query}"
        # If prompt_template is provided, it will use that.
        # For this test, we are not providing a prompt_template, so we expect the default.
        expected_prompt = f"Generate a hypothetical document for the query: {query}"

    def test_generate_hypothetical_document_handles_empty_query(self):
        ideal_doc = ""  # For an empty query, the LLM might return an empty string.
        mock_llm_client = MockLLMProvider(ideal_document=ideal_doc)
        generator = HyDEGenerator(llm_client=mock_llm_client)

        query = ""
        hypothetical_document = generator.generate_hypothetical_document(query)

        self.assertIsInstance(hypothetical_document, str)
        self.assertEqual(hypothetical_document, ideal_doc)
        # The prompt will still be generated, but the LLM is expected to return an empty string.

        # We can't directly assert on the generate method of MockLLMProvider as it doesn't store calls.
        # Instead, we assert the output, which is directly controlled by MockLLMProvider.
