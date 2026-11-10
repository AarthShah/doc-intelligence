import unittest
from unittest.mock import MagicMock

from doc_intelligence.retrieval.hyde_generator import HyDEGenerator


class TestHyDEGenerator(unittest.TestCase):
    def test_init_stores_dependencies(self):
        mock_client = MagicMock()
        prompt_template = "Custom prompt: {query}"
        generator = HyDEGenerator(llm_client=mock_client, prompt_template=prompt_template)

        self.assertEqual(generator.llm_client, mock_client)
        self.assertEqual(generator.prompt_template, prompt_template)

    def test_generate_hypothetical_document_returns_string(self):
        mock_llm_client = MagicMock()
        mock_llm_client.generate.return_value = "This is a hypothetical document."
        generator = HyDEGenerator(llm_client=mock_llm_client)

        query = "What is the capital of France?"
        hypothetical_document = generator.generate_hypothetical_document(query)

        self.assertIsInstance(hypothetical_document, str)
        mock_llm_client.generate.assert_called_once_with(
            "Generate a hypothetical document for the query: What is the capital of France?"
        )
