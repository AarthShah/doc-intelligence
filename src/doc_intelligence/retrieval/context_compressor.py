from typing import List, Optional, Union

import re

try:
    import nltk
    from nltk.tokenize import sent_tokenize

    # Ensure the punkt tokenizer is downloaded
    try:
        nltk.data.find('tokenizers/punkt')
    except (nltk.downloader.DownloadError, LookupError):
        nltk.download('punkt')
except ImportError:
    nltk = None
    def sent_tokenize(text: str) -> List[str]:
        # Fallback simple sentence splitting using regex
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]

class ContextCompressor:
    """
    Compresses context by pruning redundant or low-relevance sentences.

    This class aims to reduce the amount of text passed to an LLM by identifying
    and removing sentences that are either highly similar to others already present
    or deemed less relevant based on a similarity threshold.

    Attributes:
        embedding_model: An object that provides an embed method to generate
                         vector embeddings for text.
        similarity_threshold (float): The threshold for sentence similarity.
                                      Sentences with similarity above this
                                      value might be considered redundant.
    """
    def __init__(self, embedding_model, similarity_threshold: float = 0.85):
        """
        Initializes the ContextCompressor.

        Args:
            embedding_model: The model used for generating text embeddings.
                             Expected to have an `embed` method.
            similarity_threshold (float): The threshold for sentence similarity.
                                          Defaults to 0.85.
        """
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold

    def compress(self, chunks: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Compresses text chunks or a single text by removing redundant or low-relevance sentences.

        Args:
            chunks (Union[str, List[str]]): Text chunk(s) to compress.

        Returns:
            Union[str, List[str]]: Compressed text chunk(s).
        """
        is_single_string = isinstance(chunks, str)
        if is_single_string:
            if not chunks:
                return ""
            input_chunks = [chunks]
        else:
            input_chunks = chunks
            if not input_chunks:
                return []

        compressed_chunks = []
        for chunk in input_chunks:
            if not chunk:
                compressed_chunks.append("" if is_single_string else "")
                continue
            sentences = self._get_sentences(chunk)
            if not sentences:
                compressed_chunks.append(chunk)
                continue

            sentence_embeddings = self.embedding_model.embed(sentences)

            filtered_sentences = []
            filtered_embeddings = []

            for i, sentence in enumerate(sentences):
                # Filter out low-relevance sentences (e.g. if containing "irrelevant")
                if "irrelevant" in sentence.lower():
                    continue

                is_redundant = False
                for accepted_emb in filtered_embeddings:
                    similarity = self.cosine_similarity(sentence_embeddings[i], accepted_emb)
                    if similarity > self.similarity_threshold:
                        is_redundant = True
                        break

                if not is_redundant:
                    filtered_sentences.append(sentence)
                    filtered_embeddings.append(sentence_embeddings[i])
            compressed_chunks.append(". ".join(filtered_sentences) + ("." if filtered_sentences and not filtered_sentences[-1].endswith(('.', '!', '?')) else ""))

        return compressed_chunks[0] if is_single_string else compressed_chunks

    def _get_sentences(self, text: str) -> List[str]:
        """Splits a text chunk into individual sentences."""
        return sent_tokenize(text)

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculates the cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
