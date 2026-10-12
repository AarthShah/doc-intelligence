from typing import List, Optional, Union

import re

from doc_intelligence.retrieval.token_budget_manager import TokenBudgetManager

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
    Compresses context by pruning redundant or low-relevance sentences from text chunks.

    This class reduces the token count of retrieved context before passing it to an LLM
    by filtering out sentences that are redundant (exceeding a cosine similarity threshold)
    or deemed low-relevance.

    Attributes:
        embedding_model (object): Model providing an `embed` method for generating text embeddings.
        similarity_threshold (float): Cosine similarity cutoff above which sentences are treated as redundant.
    """
    def __init__(self, embedding_model, similarity_threshold: float = 0.85, max_tokens: int = 4096, tokenizer=None):
        """
        Initializes the ContextCompressor with an embedding model, a similarity threshold, and token budget options.

        Args:
            embedding_model (object): The model used to compute vector embeddings for sentences.
            similarity_threshold (float, optional): The threshold for sentence redundancy. Defaults to 0.85.
            max_tokens (int, optional): The maximum allowed number of tokens. Defaults to 4096.
            tokenizer (Callable[[str], List[str]], optional): A callable that tokenizes text. Defaults to whitespace tokenization.
        """
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
        resolved_tokenizer = tokenizer if tokenizer is not None else (lambda t: t.split())
        self.token_budget_manager = TokenBudgetManager(max_tokens=max_tokens, tokenizer=resolved_tokenizer)

    def compress(self, chunks: Union[str, List[str]]) -> Union[str, List[str]]:
        """
        Compresses a single text string or a list of text chunks by removing redundant and low-relevance sentences.

        Args:
            chunks (Union[str, List[str]]): A text string or a list of text strings to compress.

        Returns:
            Union[str, List[str]]: The compressed text string or list of compressed text strings.
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
            chunk_text = ". ".join(filtered_sentences) + ("." if filtered_sentences and not filtered_sentences[-1].endswith(('.', '!', '?')) else "")
            compressed_chunks.append(chunk_text)

        truncated_chunks = self.token_budget_manager.truncate(compressed_chunks)
        return truncated_chunks[0] if is_single_string else truncated_chunks

    def _get_sentences(self, text: str) -> List[str]:
        """
        Splits a text chunk into individual sentences using NLTK sentence tokenization or a regex fallback.

        Args:
            text (str): The text chunk to split.

        Returns:
            List[str]: A list of extracted sentence strings.
        """
        return sent_tokenize(text)

    def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
        """Calculates the cosine similarity between two vectors."""
        dot_product = sum(a * b for a, b in zip(vec_a, vec_b))
        norm_a = sum(a * a for a in vec_a) ** 0.5
        norm_b = sum(b * b for b in vec_b) ** 0.5
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot_product / (norm_a * norm_b)
