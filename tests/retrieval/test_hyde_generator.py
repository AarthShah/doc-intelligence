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

    def test_generate_returns_hypothetical_document(self,):
        mock_client = MagicMock()
        mock_client.generate.return_value = "This is a hypothetical document about the query."
        generator = HyDEGenerator(llm_client=mock_client)

        result = generator.generate("What is HyDE?")

        self.assertEqual(result, "This is a hypothetical document about the query.")
        mock_client.generate.assert_called_once()
