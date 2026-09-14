"""Sliding window chunker with token budget and overlap."""

from typing import List
from doc_intelligence.models import Document, Chunk


class SlidingWindowChunker:
    """Chunks text into windows with defined token overlap."""

    def __init__(self, window_size: int = 150, overlap_size: int = 30):
        if overlap_size >= window_size:
            raise ValueError("overlap_size must be strictly less than window_size")
        self.window_size = window_size
        self.overlap_size = overlap_size

    def chunk(self, document: Document) -> List[Chunk]:
        """Produce overlapping window chunks from a Document."""
        words = document.text.split()
        if not words:
            return []

        chunks: List[Chunk] = []
        step = self.window_size - self.overlap_size
        idx = 0

        for start in range(0, len(words), step):
            end = min(start + self.window_size, len(words))
            window_words = words[start:end]
            chunk_text = " ".join(window_words)

            chunks.append(
                Chunk(
                    text=chunk_text,
                    chunk_index=idx,
                    parent_doc_id=document.id,
                    token_count=len(window_words),
                    metadata={"window_start": start, "window_end": end},
                )
            )
            idx += 1
            if end >= len(words):
                break

        return chunks
