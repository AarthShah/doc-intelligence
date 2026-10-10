from collections import Counter
from typing import List, Optional
import re

from src.doc_intelligence.models import Chunk


class QueryExpander:
    """
    Expands queries using synonym networks and pseudo-relevance feedback.
    """

    def __init__(
        self,
        synonym_network: Optional[dict] = None,
        pseudo_relevance_feedback_docs: Optional[List[Chunk]] = None,
    ):
        """
        Initializes the QueryExpander.

        Args:
            synonym_network: A dictionary representing the synonym network.
            pseudo_relevance_feedback_docs: A list of Chunks to use for PRF.
        """
        self.synonym_network = synonym_network if synonym_network is not None else {}
        self.pseudo_relevance_feedback_docs = (
            pseudo_relevance_feedback_docs if pseudo_relevance_feedback_docs is not None else []
        )

    def expand_query_synonyms(self, query: str) -> str:
        """
        Expands the query using the synonym network.

        Args:
            query: The original query.

        Returns:
            The expanded query.
        """
        expanded_query = query
        words = query.split()
        for word in words:
            if word in self.synonym_network:
                synonyms = self.synonym_network[word]
                expanded_query += " " + " ".join(synonyms)
        return expanded_query

    def expand_query_prf(self, query: str) -> str:
        """
        Expands the query using pseudo-relevance feedback.

        Identifies common keywords from PRF documents to enhance the query.

        Args:
            query: The original query.

        Returns:
            The expanded query with added keywords.
        """
        if not self.pseudo_relevance_feedback_docs:
            return query

        # Simple tokenizer: split by non-alphanumeric characters
        def tokenize(text: str) -> List[str]:
            return re.findall(r'\b\w+\b', text.lower())

        # Common English stop words (a small subset for demonstration)
        stop_words = set([
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "it", "is", "and", "or", "i", "you", "he", "she", "they", "we", "me", "him", "her", "them", "us", "my", "your", "his", "its", "their", "our", "with", "by", "from", "about", "as", "be", "was", "were", "been", "are", "has", "had", "do", "does", "did", "will", "would", "should", "can", "could", "not", "no", "very", "so", "just"
        ])

        all_words = []
        for chunk in self.pseudo_relevance_feedback_docs:
            all_words.extend(tokenize(chunk.content))

        word_counts = Counter(all_words)

        # Get the most common words, excluding stop words and words from the original query
        original_query_words = set(tokenize(query))
        num_keywords_to_add = 3  # Number of keywords to add
        expanded_query_terms = []

        for word, count in word_counts.most_common():
            if word not in stop_words and word not in original_query_words:
                expanded_query_terms.append(word)
                if len(expanded_query_terms) >= num_keywords_to_add:
                    break

        return query + " " + " ".join(expanded_query_terms)
