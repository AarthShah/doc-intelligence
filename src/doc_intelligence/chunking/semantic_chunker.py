"""Semantic boundary chunker preserving paragraph and sentence coherence."""

import re
from typing import List
from doc_intelligence.models import Document, Chunk


class SemanticChunker:
    """Partitions text along sentence and paragraph boundaries."""

    SENTENCE_SPLIT_REGEX = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9])")

    def __init__(self, max_chunk_size: int = 400, min_chunk_size: int = 50):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size

    def chunk(self, document: Document) -> List[Chunk]:
        """Split a Document into coherent semantic chunks."""
        text = document.text
        if not text:
            return []

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        raw_chunks: List[str] = []

        for p in paragraphs:
            if len(p) <= self.max_chunk_size:
                raw_chunks.append(p)
            else:
                # Split large paragraph into sentences
                sentences = self.SENTENCE_SPLIT_REGEX.split(p)
                current = ""
                for s in sentences:
                    if len(current) + len(s) + 1 <= self.max_chunk_size:
                        current = f"{current} {s}".strip()
                    else:
                        if current:
                            raw_chunks.append(current)
                        current = s
                if current:
                    raw_chunks.append(current)

        # Merge undersized chunks with neighbors
        merged: List[str] = []
        buffer = ""
        for rc in raw_chunks:
            if len(buffer) + len(rc) + 1 <= self.max_chunk_size:
                buffer = f"{buffer} {rc}".strip()
            else:
                if buffer:
                    merged.append(buffer)
                buffer = rc
        if buffer:
            merged.append(buffer)

        chunks: List[Chunk] = []
        for idx, chunk_text in enumerate(merged):
            approx_tokens = len(chunk_text.split())
            chunks.append(
                Chunk(
                    text=chunk_text,
                    chunk_index=idx,
                    parent_doc_id=document.id,
                    token_count=approx_tokens,
                    metadata={"source": document.metadata.source_name},
                )
            )
        return chunks
