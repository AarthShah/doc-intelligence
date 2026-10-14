from typing import List
from doc_intelligence.retrieval.context_compressor import ContextCompressor


class DummyEmbeddingModel:
    def embed(self, texts):
        # Return unique or hash-based mock embeddings to differentiate sentences
        return [[float(hash(t) % 10) / 10.0, 0.2, 0.3] for t in texts]


def test_context_compressor_initialization():
    embedding_model = DummyEmbeddingModel()
    compressor = ContextCompressor(embedding_model=embedding_model, similarity_threshold=0.85)
    assert compressor is not None
    assert compressor.similarity_threshold == 0.85

def test_context_compressor_compress_redundant_sentences():
    embedding_model = DummyEmbeddingModel()

    class MockContextCompressor(ContextCompressor):
        def _get_sentences(self, text: str) -> List[str]:
            # Simulate sentence splitting
            return [s.strip() for s in text.split('.') if s.strip()]

        def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
            # Simulate high similarity for identical sentences
            if vec_a == vec_b:
                return 0.99  # Above threshold
            # Simulate low similarity for different sentences
            return 0.1  # Below threshold
    
    compressor = MockContextCompressor(embedding_model=embedding_model, similarity_threshold=0.85)
    
    # Text with redundant sentences
    text = "This is the first sentence. This is the first sentence. This is a different sentence. This is the first sentence."
    compressed_text = compressor.compress(text)

    # Expecting only unique sentences to remain
    expected_sentences = ["This is the first sentence", "This is a different sentence"]
    actual_sentences = [s.strip() for s in compressed_text.split('.') if s.strip()]

    assert actual_sentences == expected_sentences

def test_context_compressor_compress_low_relevance_sentences():
    embedding_model = DummyEmbeddingModel()

    class MockContextCompressor(ContextCompressor):
        def _get_sentences(self, text: str) -> List[str]:
            return [s.strip() for s in text.split('.') if s.strip()]

        def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
            # Simulate low similarity for irrelevant sentence containing "irrelevant"
            return 0.1

    compressor = MockContextCompressor(embedding_model=embedding_model, similarity_threshold=0.85)

    # Text with a mix of relevant and irrelevant sentences
    text = "This is a relevant sentence. This is another relevant sentence. This is an irrelevant sentence. This is also a relevant sentence."
    compressed_text = compressor.compress(text)

    # Expecting only relevant sentences to remain
    expected_sentences = ["This is a relevant sentence", "This is another relevant sentence", "This is also a relevant sentence"]
    actual_sentences = [s.strip() for s in compressed_text.split('.') if s.strip()]

    assert actual_sentences == expected_sentences

def test_context_compressor_compress_empty_text():
    embedding_model = DummyEmbeddingModel()
    compressor = ContextCompressor(embedding_model=embedding_model, similarity_threshold=0.85)
    compressed_text = compressor.compress("")
    assert compressed_text == ""

def test_context_compressor_compress_single_sentence():
    embedding_model = DummyEmbeddingModel()
    compressor = ContextCompressor(embedding_model=embedding_model, similarity_threshold=0.85)
    text = "This is a single sentence."
    compressed_text = compressor.compress(text)
    assert compressed_text == text.strip()

def test_context_compressor_compress_all_unique_sentences():
    embedding_model = DummyEmbeddingModel()

    class MockContextCompressor(ContextCompressor):
        def _get_sentences(self, text: str) -> List[str]:
            return [s.strip() for s in text.split('.') if s.strip()]

        def cosine_similarity(self, vec_a: List[float], vec_b: List[float]) -> float:
            # All sentences are distinct enough not to exceed the threshold
            return 0.1

    compressor = MockContextCompressor(embedding_model=embedding_model, similarity_threshold=0.85)
    text = "First unique sentence. Second unique sentence. Third unique sentence."
    compressed_text = compressor.compress(text)

    expected_sentences = ["First unique sentence", "Second unique sentence", "Third unique sentence"]
    actual_sentences = [s.strip() for s in compressed_text.split('.') if s.strip()]

    assert actual_sentences == expected_sentences
