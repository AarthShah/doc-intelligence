import unittest
from doc_intelligence.retrieval.query_expander import QueryExpander


class TestQueryExpander(unittest.TestCase):
    """Test suite for QueryExpander functionalities."""

    def test_init_default(self):
        expander = QueryExpander()
        self.assertEqual(expander.synonym_network, {})

    def test_init_with_params(self):
        synonyms = {"search": ["find", "lookup"]}
        expander = QueryExpander(synonym_network=synonyms)
        self.assertEqual(expander.synonym_network, synonyms)

    def test_expand_query_synonyms_no_network(self):
        expander = QueryExpander()
        query = "hello world"
        result = expander.expand_query_synonyms(query)
        self.assertEqual(result, query)

    def test_expand_query_synonyms_with_network(self):
        synonyms = {"quick": ["fast", "rapid"], "dog": ["hound"]}
        expander = QueryExpander(synonym_network=synonyms)
        query = "the quick dog"
        result = expander.expand_query_synonyms(query)
        # Check that synonyms are included in the expanded query
        self.assertIn("fast", result)
        self.assertIn("rapid", result)
        self.assertIn("hound", result)
        self.assertIn("quick", result)
        self.assertIn("dog", result)
