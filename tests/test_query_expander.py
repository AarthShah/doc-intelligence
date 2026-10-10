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
        self.assertEqual(result, query.split())

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

    def test_expand_query_synonyms_case_insensitive(self):
        synonyms = {"Quick": ["Fast", "Rapid"], "Dog": ["Hound"]}
        expander = QueryExpander(synonym_network=synonyms)
        query = "the quick dog"
        # The expand_query_synonyms method returns a list of strings, not a single string.
        # We need to join them for assertion.
        result_list = expander.expand_query_synonyms(query)
        result = " ".join(result_list)
        # Check that synonyms are included in the expanded query, case-insensitively
        self.assertIn("Fast", result)
        self.assertIn("Rapid", result)
        self.assertIn("Hound", result)
        self.assertIn("quick", result) # Original word should remain
        self.assertIn("dog", result)   # Original word should remain

    def test_expand_query_prf_no_docs(self):
        expander = QueryExpander()
        query = "hello world"
        result = expander.expand_query_prf(query, [])
        self.assertEqual(result, query.split())

    def test_expand_query_prf_with_docs(self):
        expander = QueryExpander()
        query = "machine learning"
        mock_docs = [
            "This document is about machine learning and artificial intelligence.",
            "Learning from data is key in machine learning.",
            "Deep learning is a subset of machine learning.",
        ]
        # Expected keywords from PRF: 'learning', 'artificial', 'intelligence', 'data', 'deep'
        # The original query terms 'machine' and 'learning' should also be included
        result = expander.expand_query_prf(query, mock_docs)
        # The result is a list of strings, so we join them for assertion.
        result_str = " ".join(result)
        self.assertIn("machine", result_str)
        self.assertIn("learning", result_str)
        self.assertIn("artificial", result_str)
        self.assertIn("intelligence", result_str)
        self.assertIn("data", result_str)
        self.assertIn("deep", result_str)

    def test_expand_query_prf_with_docs_and_synonyms(self):
        synonyms = {"ML": ["machine learning"], "AI": ["artificial intelligence"]}
        expander = QueryExpander(synonym_network=synonyms)
        query = "AI systems"
        mock_docs = [
            "AI is a field of computer science.",
            "Understanding AI systems requires knowledge of algorithms.",
            "Systems thinking is important in AI.",
        ]
        # Expected keywords from PRF: 'systems', 'computer', 'science', 'algorithms', 'thinking'
        # Also include expanded synonyms: 'artificial intelligence'
        result = expander.expand_query_prf(query, mock_docs)
        result_str = " ".join(result)
        self.assertIn("AI", result_str) # Original term
        self.assertIn("artificial intelligence", result_str) # Expanded synonym
        self.assertIn("systems", result_str)
        self.assertIn("computer", result_str)
        self.assertIn("science", result_str)
        self.assertIn("algorithms", result_str)
        self.assertIn("thinking", result_str)

    def test_combined_expand_only_synonyms(self):
        synonyms = {"search": ["find", "lookup"]}
        expander = QueryExpander(synonym_network=synonyms)
        query = "search for information"
        mock_docs = []
        # The combined_expand method should accept mock_docs, even if empty.
        result = expander.combined_expand(query, mock_docs)
        self.assertEqual(result, ["search", "for", "information", "find", "lookup"])

    def test_combined_expand_only_prf(self):
        expander = QueryExpander()
        query = "data analysis"
        mock_docs = [
            "Data analysis involves statistics.",
            "Analyzing data helps in decision making.",
            "Statistical analysis is crucial.",
        ]
        # The combined_expand method should accept mock_docs.
        result = expander.combined_expand(query, mock_docs)
        # The result is a list of strings, so we join them for assertion.
        result_str = " ".join(result)
        self.assertIn("data", result_str)
        self.assertIn("analysis", result_str)
        self.assertIn("statistics", result_str)
        self.assertIn("analyzing", result_str)
        self.assertIn("decision", result_str)
        self.assertIn("making", result_str)
        self.assertIn("statistical", result_str)

    def test_combined_expand_with_synonyms_and_prf(self):
        synonyms = {"big data": ["data science", "analytics"]}
        expander = QueryExpander(synonym_network=synonyms)
        query = "big data insights"
        mock_docs = [
            "Big data processing requires efficient algorithms.",
            "Gaining insights from big data is valuable.",
            "Data science is a field related to big data.",
        ]
        # The combined_expand method should accept mock_docs.
        result = expander.combined_expand(query, mock_docs)
        # The result is a list of strings, so we join them for assertion.
        result_str = " ".join(result)
        self.assertIn("big data", result_str) # Original term
        self.assertIn("data science", result_str) # Expanded synonym
        self.assertIn("analytics", result_str) # Expanded synonym
        self.assertIn("insights", result_str) # Original term
        self.assertIn("processing", result_str) # From PRF
        self.assertIn("efficient", result_str) # From PRF
        self.assertIn("algorithms", result_str) # From PRF
        self.assertIn("gaining", result_str) # From PRF
        self.assertIn("valuable", result_str) # From PRF

    def test_expand_query_prf_extracts_top_terms(self):
        expander = QueryExpander()
        query = "cloud computing"
        mock_docs = [
            "Cloud computing architecture relies heavily on virtualization and distributed storage.",
            "Virtualization allows cloud computing infrastructure to scale dynamically.",
            "Distributed systems are fundamental to modern cloud computing reliability."
        ]
        result = expander.expand_query_prf(query, mock_docs, top_k=3)
        result_str = " ".join(result)
        self.assertIn("cloud", result_str)
        self.assertIn("computing", result_str)
        self.assertIn("virtualization", result_str)
        self.assertIn("distributed", result_str)

    def test_combined_expand_explicit_parameters(self):
        synonyms = {"security": ["protection", "safety"]}
        expander = QueryExpander(synonym_network=synonyms)
        query = "network security"
        mock_docs = [
            "Network security firewall encryption protocols protect sensitive data.",
            "Encryption and firewalls are essential for network protection."
        ]
        result = expander.combined_expand(query, docs=mock_docs, use_synonyms=True, use_prf=True)
        result_str = " ".join(result)
        self.assertIn("network", result_str)
        self.assertIn("security", result_str)
        self.assertIn("protection", result_str)
        self.assertIn("safety", result_str)
        self.assertIn("encryption", result_str)
        self.assertIn("firewall", result_str)
