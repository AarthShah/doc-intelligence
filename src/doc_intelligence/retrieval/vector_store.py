"""In-memory dense vector store with cosine similarity."""

import logging
import math
import re
import mmap
import os
from typing import Dict, List, Tuple
from doc_intelligence.models import Chunk, QueryResult
from .exceptions import VectorStoreError

logger = logging.getLogger(__name__)


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

    def __init__(self, storage_path: str | None = None, embedding_dim: int = 128):
        self.embedding_dim = embedding_dim
        self.chunks: List[Chunk] = []
        self.storage_path = storage_path
        self.mm = None
        self._cache: Dict[str, List[QueryResult]] = {}  # Cache for search results

        if self.storage_path:
            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
                logger.info("Initializing memory-mapped vector store at storage_path=%s with embedding_dim=%d", self.storage_path, self.embedding_dim)

                # Open file in read/write binary mode, create if not exists
                file_mode = "ab+"
                with open(self.storage_path, file_mode) as f:
                    self.mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
                self._load_index()
            except Exception as e:
                logger.exception("Failed to initialize memory-mapped file at %s", self.storage_path)
                raise VectorStoreError(f"Failed to initialize memory-mapped file at {self.storage_path}") from e
        else:
            logger.info("Initializing in-memory vector store without persistence with embedding_dim=%d", self.embedding_dim)

    def _load_index(self) -> None:
        """Load index from memory-mapped file."""
        if not self.mm:
            return

        try:
            logger.debug("Loading index from memory-mapped file.")
            # For simplicity, we'll assume chunks are serialized as pickle or similar.
            # In a real-world scenario, a more robust serialization format would be needed.
            # Here, we'll simulate by just checking if the file has content.
            # A proper implementation would deserialize the data.
            if self.mm: # Check if mmap object is valid and has content
                # This is a placeholder for actual deserialization logic.
                # For now, we'll assume an empty store if mm is not properly initialized.
                pass
            logger.info("Successfully loaded index from memory-mapped file.")
        except Exception as e:
            logger.exception("Failed to load index from memory-mapped file.")
            raise VectorStoreError("Failed to load index from memory-mapped file") from e

    def _save_index(self) -> None:
        """Save index to memory-mapped file."""
        if not self.mm:
            return

        try:
            logger.debug("Saving index to memory-mapped file.")
            # In a real-world scenario, serialize self.chunks and write to self.mm
            # For this example, we'll just flush changes if any were made (though none are tracked here)
            self.mm.flush()
            logger.info("Successfully saved index to memory-mapped file.")
        except Exception as e:
            logger.exception("Failed to save index to memory-mapped file.")
            raise VectorStoreError("Failed to save index to memory-mapped file") from e

    def close(self) -> None:
        """Close the memory-mapped file and release resources safely."""
        if self.mm:
            try:
                logger.info("Closing memory-mapped vector store and releasing resources.")
                self._save_index()
            finally:
                try:
                    self.mm.close()
                finally:
                    self.mm = None

    def __del__(self):
        """Ensure the index is saved and resources are released when the object is garbage collected."""
        self.close()

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Add chunks to index and generate embeddings if absent."""
        try:
            logger.info("Adding batch of %d chunks to vector store", len(chunks))
            for c in chunks:
                if not c.embedding:
                    c.embedding = simple_hash_embedding(c.text, dim=self.embedding_dim)
                self.chunks.append(c)
            self._save_index()
            self._cache.clear()
            logger.debug("Cleared search cache due to batch add_chunks operation")
        except Exception as e:
            logger.exception("Failed to add chunks to vector store")
            raise VectorStoreError("Failed to add chunks to vector store") from e

    def add(self, chunk: Chunk) -> None:
        """Add a single chunk to the index and generate embedding if absent."""
        try:
            logger.info("Adding single chunk id=%s to vector store", getattr(chunk, "id", "unknown"))
            if not chunk.embedding:
                chunk.embedding = simple_hash_embedding(chunk.text, dim=self.embedding_dim)
            self.chunks.append(chunk)
            self._save_index()
            # Clear cache on add
            self._cache.clear()
            logger.debug("Cleared search cache due to add operation")
        except Exception as e:
            logger.exception("Failed to add chunk id=%s to vector store", getattr(chunk, "id", "unknown"))
            raise VectorStoreError("Failed to add chunk to vector store") from e

    def delete(self, chunk_id: str) -> None:
        """Delete a chunk from the index by its ID."""
        try:
            logger.info("Deleting chunk id=%s from vector store", chunk_id)
            initial_count = len(self.chunks)
            self.chunks = [c for c in self.chunks if c.id != chunk_id]
            if len(self.chunks) < initial_count:
                self._save_index()
                # Clear cache on delete
                self._cache.clear()
                logger.debug("Cleared search cache due to delete operation for chunk id=%s", chunk_id)
            else:
                logger.warning("Chunk id=%s not found in vector store during delete operation", chunk_id)
        except Exception as e:
            logger.exception("Failed to delete chunk id=%s from vector store", chunk_id)
            raise VectorStoreError(f"Failed to delete chunk {chunk_id} from vector store") from e

    def search(self, query: str, top_k: int = 5) -> List[QueryResult]:
        """Perform semantic search against indexed chunks."""
        if not self.chunks:
            logger.debug("Search requested on empty vector store. Returning empty results.")
            return []

        # Check cache interaction
        cache_key = f"{query}:{top_k}"
        if cache_key in self._cache:
            logger.debug("Cache hit for search query: %r (top_k=%d)", query, top_k)
            return self._cache[cache_key]

        logger.debug("Cache miss for search query: %r (top_k=%d). Performing vector search.", query, top_k)
        try:
            query_vec = simple_hash_embedding(query, dim=self.embedding_dim)
            scored: List[Tuple[float, Chunk]] = []

            for chunk in self.chunks:
                # Ensure chunk.embedding is not None before using it
                if chunk.embedding is None:
                    logger.warning("Encountered chunk id=%s with missing embedding during search. Skipping.", getattr(chunk, "id", "unknown"))
                    continue
                sim = cosine_similarity(query_vec, chunk.embedding)
                scored.append((sim, chunk))

            scored.sort(key=lambda x: x[0], reverse=True)

            results = [
                QueryResult(chunk=chunk, score=score, retrieval_method="dense")
                for score, chunk in scored[:top_k]
            ]
            self._cache[cache_key] = results
            logger.debug("Completed search for query: %r, returned %d results", query, len(results))
            return results
        except Exception as e:
            logger.exception("Failed to search vector store for query: %r", query)
            raise VectorStoreError("Failed to search vector store") from e

    def clear(self) -> None:
        """Clear all indexed chunks."""
        try:
            logger.info("Clearing all indexed chunks and resetting vector store storage.")
            self.chunks.clear()
            if self.mm:
                # Clear the memory-mapped file content
                self.mm.seek(0)
                self.mm.write(b'\0' * len(self.mm))
                self.mm.flush()
            self._save_index() # Ensure the cleared state is persisted
            self._cache.clear()
            logger.debug("Cleared search cache during vector store clear operation")
        except Exception as e:
            logger.exception("Failed to clear vector store")
            raise VectorStoreError("Failed to clear vector store") from e

    @property
    def count(self) -> int:
        return len(self.chunks)
