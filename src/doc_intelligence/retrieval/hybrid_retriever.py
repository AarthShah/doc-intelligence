"""Hybrid retriever combining Dense Cosine and BM25 via Reciprocal Rank Fusion (RRF)."""

from typing import Dict, List
from doc_intelligence.models import Chunk, QueryResult
from doc_intelligence.retrieval.bm25_search import BM25Retriever
from doc_intelligence.retrieval.vector_store import VectorStore


class HybridRetriever:
    """Combines semantic dense search and lexical BM25 using Reciprocal Rank Fusion."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.vector_store = VectorStore()
        self.bm25 = BM25Retriever()

    def index(self, chunks: List[Chunk]) -> None:
        """Index chunks in both dense and lexical stores."""
        self.vector_store.add_chunks(chunks)
        self.bm25.index(chunks)

    def search(self, query: str, top_k: int = 5) -> List[QueryResult]:
        """Execute hybrid search with Reciprocal Rank Fusion."""
        dense_results = self.vector_store.search(query, top_k=top_k * 2)
        bm25_results = self.bm25.search(query, top_k=top_k * 2)

        rrf_scores: Dict[str, float] = {}
        chunk_map: Dict[str, Chunk] = {}

        # Accumulate RRF scores from Dense ranking
        for rank, res in enumerate(dense_results, start=1):
            cid = res.chunk.id
            chunk_map[cid] = res.chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        # Accumulate RRF scores from BM25 ranking
        for rank, res in enumerate(bm25_results, start=1):
            cid = res.chunk.id
            chunk_map[cid] = res.chunk
            rrf_scores[cid] = rrf_scores.get(cid, 0.0) + (1.0 / (self.rrf_k + rank))

        # Sort by composite RRF score
        sorted_items = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)

        results = [
            QueryResult(chunk=chunk_map[cid], score=round(score, 5), retrieval_method="hybrid_rrf")
            for cid, score in sorted_items[:top_k]
        ]
        return results
