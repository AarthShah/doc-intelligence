from typing import List, Optional, Pattern

from src.doc_intelligence.models import Document, Chunk


class RecursiveCharacterTextSplitter:
    """
    Splits text into chunks recursively based on a hierarchy of separator patterns.

    This splitter first tries to split by the longest list of separators.
    If a chunk is still too large, it splits it by the next longest separator,
    and so on, until all chunks are within the desired size.
    """

    def __init__(
        self,
        separators: List[str] = ["\n\n", "\n", " ", ""],
        chunk_size: int = 4000,
        chunk_overlap: int = 200,
    ):
        """
        Initializes the RecursiveCharacterTextSplitter.

        Args:
            separators: A list of separator strings, ordered from most to least
                        greedy. These are used to split the text.
            chunk_size: The maximum size of each chunk.
            chunk_overlap: The maximum overlap between adjacent chunks.
        """
        if chunk_size <= 0:
            raise ValueError("chunk_size must be a positive integer.")
        if chunk_overlap < 0:
            raise ValueError("chunk_overlap must be a non-negative integer.")
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be smaller than chunk_size.")

        self.separators = separators
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_text(self, text: str) -> List[str]:
        """
        Splits a given text into chunks based on the defined separators and chunk size.

        Args:
            text: The text to split.

        Returns:
            A list of text chunks.
        """
        # If the text is empty, return an empty list.
        if not text:
            return []

        # If the text is already small enough, return it as a single chunk.
        if len(text) <= self.chunk_size:
            return [text]

        # Attempt to split the text by the defined separators, from most to least greedy.
        for i, separator in enumerate(self.separators):
            potential_chunks = self._split_with_separators(text, separator)

            # If splitting by this separator resulted in more than one chunk,
            # and if any of these chunks exceed the chunk_size,
            # we need to recursively split further.
            if len(potential_chunks) > 1:
                # Check if any chunk is too large.
                too_large_chunks = [chunk for chunk in potential_chunks if len(chunk) > self.chunk_size]
                if too_large_chunks:
                    # If there are chunks that are too large, recursively call split_text on them.
                    # We are essentially trying to split with the next separator in the hierarchy.
                    processed_chunks = []
                    for chunk in potential_chunks:
                        if len(chunk) > self.chunk_size:
                            # Recursively split the oversized chunk.
                            processed_chunks.extend(self.split_text(chunk))
                        else:
                            processed_chunks.append(chunk)
                    # Filter out any empty strings that might result from splitting.
                    return [c for c in processed_chunks if c]
                else:
                    # All chunks are within the chunk_size, return them.
                    # Overlap will be handled by the `chunk` method.
                    return potential_chunks

        # If no separator was found or if separators did not help to reduce chunk size sufficiently,
        # fall back to splitting by characters to ensure progress. This is the base case for recursion.
        return self._split_into_smaller_chunks(text, self.chunk_size)

    def _split_with_separators(self, text: str, separator: str) -> List[str]:
        """Splits a text chunk by a given separator, filtering out empty strings."""
        if separator == "":
            return list(text)
        return [chunk for chunk in text.split(separator) if chunk]

    def _split_into_smaller_chunks(
        self, text: str, target_size: int
    ) -> List[str]:
        """Splits text into chunks of a target size, respecting overlap. This is a fallback mechanism."""
        chunks = []
        start_index = 0
        while start_index < len(text):
            end_index = min(start_index + target_size, len(text))
            chunk = text[start_index:end_index]
            chunks.append(chunk)
            # Adjust start_index for overlap. If end_index is the end of the text,
            # we don't need to add overlap for the next iteration.
            if end_index == len(text):
                break
            start_index += target_size - self.chunk_overlap
        return chunks

    def chunk(self, document: Document) -> List[Chunk]:
        """
        Chunks a Document into a list of smaller Chunks.

        Args:
            document: The Document object to chunk.

        Returns:
            A list of Chunk objects.
        """
        text_chunks = self.split_text(document.content)
        chunks = []
        for i, chunk_text in enumerate(text_chunks):
            # Create a new chunk object
            chunk = Chunk(
                id=f"{document.metadata.id}-chunk-{i}",  # Simple ID generation
                content=chunk_text,
                document_metadata=document.metadata,
                # Other metadata can be added here if needed
            )
            chunks.append(chunk)
        return chunks
