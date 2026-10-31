"""Hybrid retriever combining Dense Cosine and BM25 via Reciprocal Rank Fusion (RRF)."""

import json
import logging
from typing import Dict, List
from doc_intelligence.exceptions import RetrievalError, VectorStoreError
from doc_intelligence.models import Chunk, QueryResult
from doc_intelligence.retrieval.bm25_search import BM25Retriever
from doc_intelligence.retrieval.vector_store import VectorStore


logger = logging.getLogger(__name__)


class HybridRetriever:
    """Combines semantic dense search and lexical BM25 using Reciprocal Rank Fusion."""

    def __init__(self, rrf_k: int = 60):
        self.rrf_k = rrf_k
        self.vector_store = VectorStore()
        self.bm25 = BM25Retriever()

    def index(self, chunks: List[Chunk]) -> None:
        """Index chunks in both dense and lexical stores."""
        try:
            self.vector_store.add_chunks(chunks)
            self.bm25.index(chunks)
        except (VectorStoreError, Exception) as e:
            raise RetrievalError(f"Failed to index chunks: {e}") from e

    def search(self, query: str, top_k: int = 5) -> List[QueryResult]:
        """Execute hybrid search with Reciprocal Rank Fusion."""
        logger.info(
            json.dumps({
                "event": "hybrid_search_started",
                "query": query,
                "top_k": top_k,
            })
        )

        try:
            dense_results = self.vector_store.search(query, top_k=top_k * 2)
        except VectorStoreError as e:
            raise RetrievalError(f"Vector store search failed: {e}") from e
        except Exception as e:
            raise RetrievalError(f"Unexpected error during dense search: {e}") from e

        logger.info(
            json.dumps({
                "event": "dense_search_completed",
                "query": query,
                "retrieved_count": len(dense_results),
                "chunk_ids": [res.chunk.id for res in dense_results],
            })
        )

        try:
            bm25_results = self.bm25.search(query, top_k=top_k * 2)
        except Exception as e:
            raise RetrievalError(f"BM25 search failed: {e}") from e
        logger.info(
            json.dumps({
                "event": "bm25_search_completed",
                "query": query,
                "retrieved_count": len(bm25_results),
                "chunk_ids": [res.chunk.id for res in bm25_results],
            })
        )

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

        logger.info(
            json.dumps({
                "event": "reranking_completed",
                "query": query,
                "method": "rrf",
                "final_count": len(results),
                "results": [{"chunk_id": res.chunk.id, "score": res.score} for res in results],
            })
        )

        return results

    def hybrid_search(self, query: str, top_k: int) -> List[tuple[str, str, float]]:
        """
        Performs a hybrid search using both vector store and BM25, returning
        a list of (doc_id, content, score) tuples.
        """
        results = self.search(query, top_k)
        return [(res.chunk.id, res.chunk.content, res.score) for res in results]
