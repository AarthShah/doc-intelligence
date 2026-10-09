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
        chunks = self._split(text)
        # Ensure no empty chunks are returned
        return [chunk for chunk in chunks if chunk]

    def _split(self, text: str) -> List[str]:
        """
        Recursively splits text into smaller chunks.
        """
        if len(text) <= self.chunk_size:
            return [text]

        for separator in self.separators:
            if separator == "":
                # If the separator is an empty string, split into characters
                # This is a fallback to ensure progress
                return self._split_into_smaller_chunks(text, len(text) // 2)

            if separator in text:
                potential_chunks = text.split(separator)
                if len(potential_chunks) > 1:
                    # Check if any of the split parts are larger than chunk_size
                    if any(len(chunk) > self.chunk_size for chunk in potential_chunks):
                        # If any part is too large, recursively split this part
                        # But first, try to join them back with the separator to maintain context
                        # We will split the joined text further down
                        return self._split_into_smaller_chunks(text, self.chunk_size)

                    # If all parts are within chunk_size, process them
                    # We will handle overlap in a later step or by merging appropriately
                    # For now, just return the split parts
                    return potential_chunks

        # If no separator is found, or if separators don't help, split by character
        return self._split_into_smaller_chunks(text, self.chunk_size)

    def _split_into_smaller_chunks(
        self, text: str, target_size: int
    ) -> List[str]:
        """
        Splits text into chunks of a target size, respecting overlap.
        This is a more direct splitting mechanism when recursion isn't ideal.
        """
        chunks = []
        start_index = 0
        while start_index < len(text):
            end_index = min(start_index + target_size, len(text))
            chunk = text[start_index:end_index]
            chunks.append(chunk)
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
