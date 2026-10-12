from typing import List, Optional

import nltk
from nltk.tokenize import sent_tokenize

# Ensure the punkt tokenizer is downloaded
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

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

    def compress(self, chunks: List[str]) -> List[str]:
        """
        Compresses a list of text chunks by removing redundant or low-relevance sentences.

        Args:
            chunks (List[str]): A list of text chunks to compress.

        Returns:
            List[str]: A list of compressed text chunks.
        """
        compressed_chunks = []
        for chunk in chunks:
            # In a real implementation, this would involve:
            # 1. Splitting the chunk into sentences.
            # 2. Embedding each sentence.
            # 3. Calculating pairwise similarities.
            # 4. Identifying and removing redundant/low-relevance sentences.
            # For this initial step, we'll return the chunk as is.
            compressed_chunks.append(chunk)
        compressed_chunks = []
        for chunk in chunks:
            sentences = sent_tokenize(chunk)
            if not sentences:
                continue

            sentence_embeddings = self.embedding_model.embed(sentences)

            # Keep track of sentences to remove
            sentences_to_remove = set()

            for i in range(len(sentences)):
                if i in sentences_to_remove:
                    continue
                for j in range(i + 1, len(sentences)):
                    if j in sentences_to_remove:
                        continue

                    # Calculate cosine similarity
                    similarity = self.cosine_similarity(
                        sentence_embeddings[i], sentence_embeddings[j]
                    )

                    if similarity > self.similarity_threshold:
                        sentences_to_remove.add(j)

            # Reconstruct the chunk with non-redundant sentences
            filtered_sentences = [
                sentence for idx, sentence in enumerate(sentences) if idx not in sentences_to_remove
            ]
            compressed_chunks.append(" ".join(filtered_sentences))

        return compressed_chunks

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculates the cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
