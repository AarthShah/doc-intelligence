"""BM25 lexical ranking retrieval."""

import math
import re
from typing import Dict, List, Set, Tuple
from doc_intelligence.models import Chunk, QueryResult


class BM25Retriever:
    """Best Matching 25 (BM25) probabilistic relevance ranking."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunks: List[Chunk] = []
        self.doc_freqs: Dict[str, int] = {}
        self.doc_lengths: List[int] = []
        self.avg_doc_length: float = 0.0

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def index(self, chunks: List[Chunk]) -> None:
        """Build BM25 inverted index from chunks."""
        self.chunks = list(chunks)
        self.doc_lengths = []
        self.doc_freqs.clear()

        for chunk in self.chunks:
            tokens = self._tokenize(chunk.text)
            self.doc_lengths.append(len(tokens))
            unique_terms = set(tokens)
            for term in unique_terms:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        total_docs = len(self.chunks)
        self.avg_doc_length = sum(self.doc_lengths) / total_docs if total_docs > 0 else 0.0

    def search(self, query: str, top_k: int = 5) -> List[QueryResult]:
        """Rank chunks by BM25 query relevance."""
        query_tokens = self._tokenize(query)
        if not self.chunks or not query_tokens:
            return []

        n_docs = len(self.chunks)
        scores: List[Tuple[float, Chunk]] = []

        for idx, chunk in enumerate(self.chunks):
            doc_tokens = self._tokenize(chunk.text)
            doc_len = self.doc_lengths[idx]
            score = 0.0

            # Count term frequencies
            tf_map: Dict[str, int] = {}
            for t in doc_tokens:
                tf_map[t] = tf_map.get(t, 0) + 1

            for qt in query_tokens:
                if qt not in tf_map:
                    continue

                df = self.doc_freqs.get(qt, 0)
                # BM25 standard IDF with smoothing
                idf = math.log((n_docs - df + 0.5) / (df + 0.5) + 1.0)

                tf = tf_map[qt]
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / (self.avg_doc_length or 1.0)))
                term_score = idf * ((tf * (self.k1 + 1.0)) / denom)
                score += term_score

            scores.append((score, chunk))

        scores.sort(key=lambda x: x[0], reverse=True)

        return [
            QueryResult(chunk=chunk, score=round(score, 4), retrieval_method="bm25")
            for score, chunk in scores[:top_k]
            if score > 0.0
        ]
