"""In-memory dense vector store with cosine similarity."""

import math
import re
import mmap
import os
from typing import Dict, List, Tuple
from doc_intelligence.models import Chunk, QueryResult
from .exceptions import VectorStoreError


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

        if self.storage_path:
            try:
                # Ensure the directory exists
                os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)

                # Open file in read/write binary mode, create if not exists
                file_mode = "ab+"
                with open(self.storage_path, file_mode) as f:
                    self.mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_WRITE)
                self._load_index()
            except Exception as e:
                raise VectorStoreError(f"Failed to initialize memory-mapped file at {self.storage_path}") from e
        else:
            # If no storage path, it's an in-memory store without persistence
            pass

    def _load_index(self) -> None:
        """Load index from memory-mapped file."""
        if not self.mm:
            return

        try:
            # For simplicity, we'll assume chunks are serialized as pickle or similar.
            # In a real-world scenario, a more robust serialization format would be needed.
            # Here, we'll simulate by just checking if the file has content.
            # A proper implementation would deserialize the data.
            if self.mm: # Check if mmap object is valid and has content
                # This is a placeholder for actual deserialization logic.
                # For now, we'll assume an empty store if mm is not properly initialized.
                pass

        except Exception as e:
            raise VectorStoreError("Failed to load index from memory-mapped file") from e

    def _save_index(self) -> None:
        """Save index to memory-mapped file."""
        if not self.mm:
            return

        try:
            # In a real-world scenario, serialize self.chunks and write to self.mm
            # For this example, we'll just flush changes if any were made (though none are tracked here)
            self.mm.flush()
        except Exception as e:
            raise VectorStoreError("Failed to save index to memory-mapped file") from e

    def __del__(self):
        """Ensure the index is saved when the object is garbage collected."""
        if self.mm:
            self._save_index()
            self.mm.close()

    def add_chunks(self, chunks: List[Chunk]) -> None:
        """Add chunks to index and generate embeddings if absent."""
        try:
            for c in chunks:
                if not c.embedding:
                    c.embedding = simple_hash_embedding(c.text, dim=self.embedding_dim)
                self.chunks.append(c)
        except Exception as e:
            raise VectorStoreError("Failed to add chunks to vector store") from e

    def search(self, query: str, top_k: int = 5) -> List[QueryResult]:
        """Perform semantic search against indexed chunks."""
        if not self.chunks:
            return []

        try:
            query_vec = simple_hash_embedding(query, dim=self.embedding_dim)
            scored: List[Tuple[float, Chunk]] = []

            for chunk in self.chunks:
                # Ensure chunk.embedding is not None before using it
                if chunk.embedding is None:
                    # Handle the case where embedding is missing, e.g., skip or log a warning
                    continue
                sim = cosine_similarity(query_vec, chunk.embedding)
                scored.append((sim, chunk))

            scored.sort(key=lambda x: x[0], reverse=True)

            results = [
                QueryResult(chunk=chunk, score=score, retrieval_method="dense")
                for score, chunk in scored[:top_k]
            ]
            return results
        except Exception as e:
            raise VectorStoreError("Failed to search vector store") from e

    def clear(self) -> None:
        """Clear all indexed chunks."""
        try:
            self.chunks.clear()
            if self.mm:
                # Clear the memory-mapped file content
                self.mm.seek(0)
                self.mm.write(b'\0' * len(self.mm))
                self.mm.flush()
        except Exception as e:
            raise VectorStoreError("Failed to clear vector store") from e

    @property
    def count(self) -> int:
        return len(self.chunks)
