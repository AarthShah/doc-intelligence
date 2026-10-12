from doc_intelligence.retrieval.context_compressor import ContextCompressor


class DummyEmbeddingModel:
    def embed(self, texts):
        return [[0.1, 0.2, 0.3] for _ in texts]


def test_context_compressor_initialization():
    embedding_model = DummyEmbeddingModel()
    compressor = ContextCompressor(embedding_model=embedding_model, similarity_threshold=0.85)
    assert compressor is not None
    assert compressor.similarity_threshold == 0.85
