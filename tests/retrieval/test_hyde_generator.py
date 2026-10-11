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
