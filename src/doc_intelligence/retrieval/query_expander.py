from collections import Counter
from typing import Any, List, Optional
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

    def expand_query_synonyms(self, query: str, max_synonyms: Optional[int] = None) -> List[str]:
        """
        Expands the query using the synonym network.

        Args:
            query: The original query.
            max_synonyms: Maximum number of synonyms to add per matched term.

        Returns:
            A list of query terms including expanded synonyms.
        """
        terms = query.split()
        if not self.synonym_network:
            return terms

        added_terms = []
        query_lower = query.lower()

        for key, synonyms in self.synonym_network.items():
            try:
                if key.lower() in query_lower:
                    syn_count = 0
                    for syn in synonyms:
                        if max_synonyms is not None and syn_count >= max_synonyms:
                            break
                        if syn not in terms and syn not in added_terms:
                            added_terms.append(syn)
                            syn_count += 1
            except Exception:
                continue

        for word in terms:
            matched_key = None
            if word in self.synonym_network:
                matched_key = word
            else:
                for k in self.synonym_network:
                    try:
                        if k.lower() == word.lower():
                            matched_key = k
                            break
                    except Exception:
                        continue
            if matched_key is not None:
                synonyms = self.synonym_network[matched_key]
                syn_count = 0
                for syn in synonyms:
                    if max_synonyms is not None and syn_count >= max_synonyms:
                        break
                    if syn not in terms and syn not in added_terms:
                        added_terms.append(syn)
                        syn_count += 1

        return terms + added_terms

    def expand_query_prf(self, query: Any, docs: Optional[List[Any]] = None, top_k: int = 10, top_k_keywords: Optional[int] = None) -> List[str]:
        """
        Expands the query using pseudo-relevance feedback.

        Identifies common keywords from PRF documents to enhance the query.

        Args:
            query: The original query (str or list of terms).
            docs: Optional list of documents (Chunks or strings) to use for PRF.
            top_k: Number of keywords to add.

        Returns:
            A list of query terms including PRF keywords.
        """
        if isinstance(query, str):
            terms = self.expand_query_synonyms(query)
        elif isinstance(query, list):
            terms = list(query)
        else:
            terms = query.split() if query else []

        feedback_docs = docs if docs is not None else self.pseudo_relevance_feedback_docs
        if not feedback_docs:
            return terms

        def tokenize(text: str) -> List[str]:
            return re.findall(r'\b\w+\b', text.lower())

        stop_words = set([
            "a", "an", "the", "in", "on", "at", "to", "for", "of", "it", "is", "and", "or", "i", "you", "he", "she", "they", "we", "me", "him", "her", "them", "us", "my", "your", "his", "its", "their", "our", "with", "by", "from", "about", "as", "be", "was", "were", "been", "are", "has", "had", "do", "does", "did", "will", "would", "should", "can", "could", "not", "no", "very", "so", "just", "this", "that", "these", "those"
        ])

        doc_tokens_list = []
        for doc in feedback_docs:
            content = doc.content if hasattr(doc, "content") else str(doc)
            tokens = [t for t in tokenize(content) if t not in stop_words and len(t) > 1]
            doc_tokens_list.append(tokens)

        if not doc_tokens_list:
            return terms

        # Compute TF-IDF-like keyword scoring across PRF documents
        num_docs = len(doc_tokens_list)
        df = Counter()
        tf_list = []
        for tokens in doc_tokens_list:
            tf = Counter(tokens)
            tf_list.append(tf)
            for word in tf.keys():
                df[word] += 1

        import math
        keyword_scores = Counter()
        for tf in tf_list:
            doc_len = sum(tf.values()) or 1
            for word, freq in tf.items():
                if df[word] > 0:
                    tf_val = freq / doc_len
                    idf_val = math.log(1.0 + (num_docs / df[word]))
                    keyword_scores[word] += tf_val * idf_val

        original_query_words = {t.lower() for t in terms}
        for t in terms:
            for w in tokenize(t):
                original_query_words.add(w)

        limit = top_k_keywords if top_k_keywords is not None else top_k

        expanded_query_terms = []
        for word, score in keyword_scores.most_common():
            if word not in original_query_words and word not in terms:
                expanded_query_terms.append(word)
                original_query_words.add(word)
                if len(expanded_query_terms) >= limit:
                    break

        return terms + expanded_query_terms

    def combined_expand(
        self,
        query: str,
        docs: Optional[List[Any]] = None,
        use_synonyms: bool = True,
        use_prf: bool = True,
        top_k: int = 10,
        max_synonyms: Optional[int] = None,
        top_k_keywords: Optional[int] = None,
    ) -> List[str]:
        """
        Expands the query using both synonym network and pseudo-relevance feedback sequentially.

        Args:
            query: The original query.
            docs: Optional list of documents for PRF.
            use_synonyms: Whether to apply synonym expansion.
            use_prf: Whether to apply PRF expansion.
            top_k: Number of keywords to add for PRF.
            max_synonyms: Maximum number of synonyms to add per matched term.
            top_k_keywords: Control number of keywords extracted for PRF.

        Returns:
            A list of fully expanded query terms.
        """
        terms = query.split()
        if use_synonyms:
            terms = self.expand_query_synonyms(query, max_synonyms=max_synonyms)
        if use_prf:
            terms = self.expand_query_prf(terms, docs=docs, top_k=top_k, top_k_keywords=top_k_keywords)
        return terms
