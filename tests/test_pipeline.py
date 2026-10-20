"""Comprehensive unit tests for doc-intelligence end-to-end pipeline."""

import unittest
import unittest
from typing import List
from unittest.mock import MagicMock, patch

from doc_intelligence.models import Document, DocumentMetadata
from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.ingestion.markdown_parser import MarkdownParser
from doc_intelligence.chunking.semantic_chunker import SemanticChunker
from doc_intelligence.chunking.sliding_window import SlidingWindowChunker
from doc_intelligence.retrieval.vector_store import VectorStore
from doc_intelligence.retrieval.bm25_search import BM25Retriever
from doc_intelligence.retrieval.hybrid_retriever import HybridRetriever
from doc_intelligence.evaluation.rag_evaluator import RAGEvaluator
from doc_intelligence.evaluation.mock_llm_provider import MockLLMProvider


import sys
from unittest.mock import MagicMock

# Ensure sentence_transformers is mocked if not installed
if "sentence_transformers" not in sys.modules:
    sys.modules["sentence_transformers"] = MagicMock()


# Mock SentenceTransformer and util for testing
class MockSentenceTransformer:
    def __init__(self, model_name: str):
        pass

    def encode(self, text: str, convert_to_tensor: bool = False) -> List[float]:
        # Return a dummy embedding based on text length for stable sorting in tests
        return [float(len(text) % 100) / 100.0, 0.5, 0.1]


class MockUtil:
    @staticmethod
    def pytorch_cos_sim(a: List[float], b: List[float]) -> List[List[float]]:
        # Simulate cosine similarity based on input length for stable sorting
        score = (1.0 - abs(len(a) - len(b)) / 100.0) * 0.95
        return [[score]]


class MockEvaluator:
    def evaluate(self, query: str, context: List[str], answer: str):
        class MockReport:
            def __init__(self, faithfulness, hallucination):
                self.faithfulness_score = faithfulness
                self.hallucination_score = hallucination
        return MockReport(0.9, 0.1)


@patch("sentence_transformers.SentenceTransformer", MockSentenceTransformer)
@patch("sentence_transformers.util", MockUtil())
class TestDocIntelligencePipeline(unittest.TestCase):
    """Test suite covering ingestion, chunking, retrieval, and evaluation."""

    def setUp(self):
        self.sample_text = (
            "Artificial intelligence systems rely heavily on high-quality training datasets.\n\n"
            "Retrieval-Augmented Generation (RAG) is an architectural pattern that enhances "
            "large language model generation by grounding answers in authoritative external knowledge.\n\n"
            "By retrieving relevant document snippets prior to generation, RAG minimizes hallucinations "
            "and provides verifiable provenance for enterprise applications."
        )
        self.sample_md = (
            "# System Architecture\n"
            "This document outlines the design.\n\n"
            "## Data Ingestion\n"
            "Ingestion normalizes documents.\n\n"
            "## Evaluation\n"
            "Metrics ensure faithfulness."
        )

    def test_text_parser(self):
        parser = TextParser()
        doc = parser.parse(self.sample_text, source_name="test_text")
        self.assertEqual(doc.metadata.source_name, "test_text")
        self.assertEqual(doc.metadata.format, "plaintext")
        self.assertGreater(len(doc.text), 50)

    def test_markdown_parser(self):
        parser = MarkdownParser()
        doc = parser.parse(self.sample_md, source_name="arch.md")
        self.assertEqual(doc.metadata.format, "markdown")
        self.assertEqual(doc.metadata.custom["heading_count"], 3)
        self.assertIn("System Architecture", doc.metadata.custom["headings"])

    def test_semantic_chunker(self):
        parser = TextParser()
        doc = parser.parse(self.sample_text)
        chunker = SemanticChunker(max_chunk_size=180)
        chunks = chunker.chunk(doc)

        self.assertGreaterEqual(len(chunks), 2)
        for c in chunks:
            self.assertEqual(c.parent_doc_id, doc.id)
            self.assertGreater(c.token_count, 0)

    def test_sliding_window_chunker(self):
        parser = TextParser()
        doc = parser.parse(self.sample_text)
        chunker = SlidingWindowChunker(window_size=20, overlap_size=5)
        chunks = chunker.chunk(doc)

        self.assertGreaterEqual(len(chunks), 2)
        self.assertEqual(chunks[0].chunk_index, 0)
        self.assertEqual(chunks[1].chunk_index, 1)

    def test_dense_vector_store(self):
        parser = TextParser()
        doc = parser.parse(self.sample_text)
        chunker = SemanticChunker(max_chunk_size=200)
        chunks = chunker.chunk(doc)

        store = VectorStore()
        store.add_chunks(chunks)
        self.assertEqual(store.count, len(chunks))

        results = store.search("retrieval augmented generation", top_k=2)
        self.assertEqual(len(results), 2)
        self.assertGreater(results[0].score, 0.0)

    def test_bm25_retriever(self):
        parser = TextParser()
        doc = parser.parse(self.sample_text)
        chunker = SemanticChunker(max_chunk_size=200)
        chunks = chunker.chunk(doc)

        bm25 = BM25Retriever()
        bm25.index(chunks)

        results = bm25.search("hallucinations", top_k=1)
        self.assertGreater(len(results), 0)
        self.assertIn("hallucinations", results[0].chunk.text.lower())

    def test_hybrid_retriever_rrf(self):
        parser = TextParser()
        doc = parser.parse(self.sample_text)
        chunker = SemanticChunker(max_chunk_size=200)
        chunks = chunker.chunk(doc)

        hybrid = HybridRetriever()
        hybrid.index(chunks)

        results = hybrid.search("RAG minimizes hallucinations", top_k=2)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].retrieval_method, "hybrid_rrf")

    def test_rag_evaluator_faithful_answer(self):
        evaluator = RAGEvaluator()
        context = ["RAG minimizes hallucinations by retrieving relevant context."]
        answer = "RAG minimizes hallucinations through relevant context retrieval."

        report = evaluator.evaluate(
            query="How does RAG help?",
            context=context,
            answer=answer,
        )
        self.assertGreaterEqual(report.faithfulness_score, 0.70)
        self.assertLessEqual(report.hallucination_score, 0.30)

    def test_rag_evaluator_hallucinated_answer(self):
        evaluator = RAGEvaluator()
        context = ["Apples and oranges are nutritious fruits."]
        hallucinated_answer = "Quantum supercomputers solve cryptographic equations in milliseconds."

        report = evaluator.evaluate(
            query="Tell me about computing.",
            context=context,
            answer=hallucinated_answer,
        )
        # Low faithfulness, high hallucination score
        self.assertLess(report.faithfulness_score, 0.30)
        self.assertGreater(report.hallucination_score, 0.70)


if __name__ == "__main__":
    unittest.main()
"""Integration tests for the full query-to-context transformation pipeline."""

import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from doc_intelligence.models import Document, DocumentMetadata
from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.chunking.semantic_chunker import SemanticChunker
from doc_intelligence.retrieval.hybrid_retriever import HybridRetriever


class TestQueryToContextPipeline(unittest.TestCase):
    """Test suite for end-to-end query-to-context transformation pipeline."""

    def setUp(self):
        self.app = FastAPI()

        @self.app.post("/query")
        def query_pipeline(payload: dict):
            query = payload.get("query", "")
            results = self.retriever.search(query, top_k=2)
            return {"results": [{"text": r.chunk.text, "score": r.score} for r in results]}

        self.client = TestClient(self.app)

        parser = TextParser()
        sample_text = (
            "FastAPI provides high performance and automatic documentation.\n\n"
            "Retrieval-Augmented Generation enhances LLM responses using external context."
        )
        doc = parser.parse(sample_text, source_name="integration_test")
        chunker = SemanticChunker(max_chunk_size=150)
        chunks = chunker.chunk(doc)

        self.retriever = HybridRetriever()
        self.retriever.index(chunks)

    def test_document_ingestion_and_vector_store_pipeline(self):
        """Test document ingestion, parsing, chunking, and storing in vector store end-to-end."""
        parser = TextParser()
        raw_text = (
            "Enterprise search systems require robust document processing.\n\n"
            "Vector databases enable efficient semantic similarity lookups."
        )
        doc = parser.parse(raw_text, source_name="ingestion_pipeline_test")
        self.assertEqual(doc.metadata.source_name, "ingestion_pipeline_test")

        chunker = SemanticChunker(max_chunk_size=100)
        chunks = chunker.chunk(doc)
        self.assertGreaterEqual(len(chunks), 1)

        from doc_intelligence.retrieval.vector_store import VectorStore
        store = VectorStore()
        store.add_chunks(chunks)
        self.assertEqual(store.count, len(chunks))

        results = store.search("vector databases", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("Vector databases", results[0].chunk.text)

    def test_query_to_context_endpoint(self):
        response = self.client.post("/query", json={"query": "FastAPI performance"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 1)
        self.assertIn("FastAPI", data["results"][0]["text"])

    def test_hybrid_retrieval_component_integration(self):
        """Test the hybrid retriever with both semantic and keyword matching capabilities."""
        results = self.retriever.search("Retrieval-Augmented Generation", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertGreater(results[0].score, 0.0)
        self.assertIn("Retrieval-Augmented Generation", results[0].chunk.text)

    def test_retrieval_with_context_compression(self):
        """Test integration of retrieval with context compression to handle token limits."""
        from doc_intelligence.retrieval.context_compressor import ContextCompressor
        from doc_intelligence.retrieval.token_budget_manager import TokenBudgetManager

        results = self.retriever.search("FastAPI performance", top_k=2)
        contexts = [r.chunk.text for r in results]

        mock_embedding_model = MagicMock()
        compressor = ContextCompressor(max_tokens=15, embedding_model=mock_embedding_model)

        compressed_contexts = compressor.compress(contexts)
        self.assertLessEqual(len(compressed_contexts), len(contexts))
        total_tokens = sum(len(c.split()) for c in compressed_contexts)
        self.assertLessEqual(total_tokens, 15)

    def test_full_pipeline_end_to_end(self):
        """Test full pipeline: ingestion, retrieval, and compression for LLM consumption."""
        from doc_intelligence.retrieval.context_compressor import ContextCompressor

        # 1. Ingest and index
        parser = TextParser()
        doc = parser.parse("RAG systems improve accuracy.", source_name="pipeline_test")
        chunker = SemanticChunker(max_chunk_size=50)
        chunks = chunker.chunk(doc)
        self.retriever.index(chunks)

        # 2. Retrieve
        results = self.retriever.search("RAG systems", top_k=1)
        contexts = [r.chunk.text for r in results]

        # 3. Compress
        mock_embedding_model = MagicMock()
        compressor = ContextCompressor(max_tokens=20, embedding_model=mock_embedding_model)
        compressed = compressor.compress(contexts)

        # 4. Assert
        self.assertTrue(len(compressed) > 0)
        self.assertIsInstance(compressed[0], str)
        self.assertLessEqual(len(compressed[0].split()), 20)

    def test_full_pipeline_with_mocks(self):
        """Test full pipeline orchestration using mocks."""
        # 1. Ingest and index
        parser = TextParser()
        doc = parser.parse("RAG systems improve accuracy.", source_name="pipeline_test")
        chunker = SemanticChunker(max_chunk_size=50)
        chunks = chunker.chunk(doc)
        self.retriever.index(chunks)

        # 2. Retrieve
        results = self.retriever.search("RAG systems", top_k=1)
        contexts = [r.chunk.text for r in results]

        # 3. Mock LLM and Evaluator
        llm = MockLLMProvider(prompt_response_map={"RAG systems improve accuracy.": "Mocked response"})
        evaluator = MockEvaluator()

        # 4. Orchestrate
        answer = llm.generate_response("RAG systems improve accuracy.")
        report = evaluator.evaluate("RAG systems", contexts, answer)

        # 5. Assert
        self.assertEqual(answer, "Mocked response")
        self.assertEqual(report.faithfulness_score, 0.9)

    def test_document_ingestion(self):
        """Test document ingestion and parsing using a simple text document."""
        parser = TextParser()
        sample_text = "This is a test document for ingestion."
        doc = parser.parse(sample_text, source_name="test_ingestion.txt")

        self.assertIsInstance(doc, Document)
        self.assertEqual(doc.metadata.source_name, "test_ingestion.txt")
        self.assertEqual(doc.metadata.format, "plaintext")
        self.assertEqual(doc.text, sample_text)
        self.assertIsNotNone(doc.id)
        self.assertIsNotNone(doc.creation_time)


if __name__ == "__main__":
    unittest.main()
"""Integration tests for the full query-to-context transformation pipeline."""

import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from doc_intelligence.models import Document, DocumentMetadata
from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.chunking.semantic_chunker import SemanticChunker
from doc_intelligence.retrieval.hybrid_retriever import HybridRetriever


class TestQueryToContextPipeline(unittest.TestCase):
    """Test suite for end-to-end query-to-context transformation pipeline."""

    def setUp(self):
        self.app = FastAPI()

        @self.app.post("/query")
        def query_pipeline(payload: dict):
            query = payload.get("query", "")
            results = self.retriever.search(query, top_k=2)
            return {"results": [{"text": r.chunk.text, "score": r.score} for r in results]}

        self.client = TestClient(self.app)

        parser = TextParser()
        sample_text = (
            "FastAPI provides high performance and automatic documentation.\n\n"
            "Retrieval-Augmented Generation enhances LLM responses using external context."
        )
        doc = parser.parse(sample_text, source_name="integration_test")
        chunker = SemanticChunker(max_chunk_size=150)
        chunks = chunker.chunk(doc)

        self.retriever = HybridRetriever()
        self.retriever.index(chunks)

    def test_document_ingestion_and_vector_store_pipeline(self):
        """Test document ingestion, parsing, chunking, and storing in vector store end-to-end."""
        parser = TextParser()
        raw_text = (
            "Enterprise search systems require robust document processing.\n\n"
            "Vector databases enable efficient semantic similarity lookups."
        )
        doc = parser.parse(raw_text, source_name="ingestion_pipeline_test")
        self.assertEqual(doc.metadata.source_name, "ingestion_pipeline_test")

        chunker = SemanticChunker(max_chunk_size=100)
        chunks = chunker.chunk(doc)
        self.assertGreaterEqual(len(chunks), 1)

        from doc_intelligence.retrieval.vector_store import VectorStore
        store = VectorStore()
        store.add_chunks(chunks)
        self.assertEqual(store.count, len(chunks))

        results = store.search("vector databases", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertIn("Vector databases", results[0].chunk.text)

    def test_query_to_context_endpoint(self):
        response = self.client.post("/query", json={"query": "FastAPI performance"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("results", data)
        self.assertGreaterEqual(len(data["results"]), 1)
        self.assertIn("FastAPI", data["results"][0]["text"])

    def test_hybrid_retrieval_component_integration(self):
        """Test the hybrid retriever with both semantic and keyword matching capabilities."""
        results = self.retriever.search("Retrieval-Augmented Generation", top_k=1)
        self.assertEqual(len(results), 1)
        self.assertGreater(results[0].score, 0.0)
        self.assertIn("Retrieval-Augmented Generation", results[0].chunk.text)

    def test_retrieval_with_context_compression(self):
        """Test integration of retrieval with context compression to handle token limits."""
        from doc_intelligence.retrieval.context_compressor import ContextCompressor
        from doc_intelligence.retrieval.token_budget_manager import TokenBudgetManager

        results = self.retriever.search("FastAPI performance", top_k=2)
        contexts = [r.chunk.text for r in results]

        mock_embedding_model = MagicMock()
        compressor = ContextCompressor(max_tokens=15, embedding_model=mock_embedding_model)

        compressed_contexts = compressor.compress(contexts)
        self.assertLessEqual(len(compressed_contexts), len(contexts))
        total_tokens = sum(len(c.split()) for c in compressed_contexts)
        self.assertLessEqual(total_tokens, 15)

    def test_full_pipeline_end_to_end(self):
        """Test full pipeline: ingestion, retrieval, and compression for LLM consumption."""
        from doc_intelligence.retrieval.context_compressor import ContextCompressor

        # 1. Ingest and index
        parser = TextParser()
        doc = parser.parse("RAG systems improve accuracy.", source_name="pipeline_test")
        chunker = SemanticChunker(max_chunk_size=50)
        chunks = chunker.chunk(doc)
        self.retriever.index(chunks)

        # 2. Retrieve
        results = self.retriever.search("RAG systems", top_k=1)
        contexts = [r.chunk.text for r in results]

        # 3. Compress
        mock_embedding_model = MagicMock()
        compressor = ContextCompressor(max_tokens=20, embedding_model=mock_embedding_model)
        compressed = compressor.compress(contexts)

        # 4. Assert
        self.assertTrue(len(compressed) > 0)
        self.assertIsInstance(compressed[0], str)
        self.assertLessEqual(len(compressed[0].split()), 20)

    def test_full_pipeline_with_mocks(self):
        """Test full pipeline orchestration using mocks."""
        # 1. Ingest and index
        parser = TextParser()
        doc = parser.parse("RAG systems improve accuracy.", source_name="pipeline_test")
        chunker = SemanticChunker(max_chunk_size=50)
        chunks = chunker.chunk(doc)
        self.retriever.index(chunks)

        # 2. Retrieve
        results = self.retriever.search("RAG systems", top_k=1)
        contexts = [r.chunk.text for r in results]

        # 3. Mock LLM and Evaluator
        llm = MockLLMProvider(prompt_response_map={"RAG systems improve accuracy.": "Mocked response"})
        evaluator = MockEvaluator()

        # 4. Orchestrate
        answer = llm.generate_response("RAG systems improve accuracy.")
        report = evaluator.evaluate("RAG systems", contexts, answer)

        # 5. Assert
        self.assertEqual(answer, "Mocked response")
        self.assertEqual(report.faithfulness_score, 0.9)

    def test_semantic_chunking_process(self):
        """Test the semantic chunking process after document ingestion."""
        parser = TextParser()
        sample_text = (
            "This is the first sentence of a sample document. "
            "It contains several sentences to test the chunking process. "
            "Semantic chunking aims to create meaningful segments of text. "
            "Each chunk should ideally represent a coherent piece of information. "
            "This is the final sentence of the sample document."
        )
        doc = parser.parse(sample_text, source_name="semantic_chunking_test")
        chunker = SemanticChunker(max_chunk_size=60)  # Adjust size as needed
        chunks = chunker.chunk(doc)

        self.assertGreater(len(chunks), 1, "Document should be split into multiple chunks.")
        # Assert that chunks are not empty and retain parent document ID
        for chunk in chunks:
            self.assertTrue(len(chunk.text) > 0, "Chunk text should not be empty.")
            self.assertEqual(chunk.parent_doc_id, doc.id, "Chunk should reference its parent document.")
        # This assertion might need adjustment based on the exact behavior of SemanticChunker
        # with the given max_chunk_size and sample text. For this example, let's assume
        # it should produce at least 2 chunks for the given text and size.
        self.assertGreaterEqual(len(chunks), 2, "Expected at least two semantic chunks.")


if __name__ == "__main__":
    unittest.main()
