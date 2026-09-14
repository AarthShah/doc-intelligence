"""In-memory dense vector store with cosine similarity."""

import math
import re
from typing import Dict, List, Tuple
from doc_intelligence.models import Chunk, QueryResult


def simple_hash_embedding(text: str, dim: int = 128) -> List[float]:
    """Deterministic hash embedding mapping text tokens to a normalized dense vector."""
    vector = [0.0] * dim
    tokens = re.findall(r"\b\w+\b", text.lower())
    if not tokens:
        return vector

    for token in tokens:
        idx = hash(token) % dim
        vector[idx] += 1.0

    # L2 normalize
    norm = math.sqrt(sum(x * x for x in vector))
    if norm > 0:
        vector = [x / norm for x in vector]
    return vector


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if len(vec_a) != len(vec_b):
        return 0.0
    dot = sum(a * b for a, b in zip(vec_a, vec_b))
    return max(0.0, min(1.0, dot))


class VectorStore:
    """In-memory vector store indexed by cosine similarity."""

    def __init__(self, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.chunks: List[Chunk] = []

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Add chunks to index and generate embeddings if absent."""
        for c in chunks:
            if not c.embedding:
                c.embedding = simple_hash_embedding(c.text, dim=self.embedding_dim)
            self.chunks.append(c)

    def search(self, query: str, top_k: int = 5) -> List[QueryResult]:
        """Perform semantic search against indexed chunks."""
        if not self.chunks:
            return []

        query_vec = simple_hash_embedding(query, dim=self.embedding_dim)
        scored: List[Tuple[float, Chunk]] = []

        for chunk in self.chunks:
            sim = cosine_similarity(query_vec, chunk.embedding or [])
            scored.append((sim, chunk))

        scored.sort(key=lambda x: x[0], reverse=True)

        results = [
            QueryResult(chunk=chunk, score=score, retrieval_method="dense")
            for score, chunk in scored[:top_k]
        ]
        return results

    def clear(self) -> None:
        """Clear all indexed chunks."""
        self.chunks.clear()

    @property
    def count(self) -> int:
        return len(self.chunks)
