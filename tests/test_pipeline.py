"""Comprehensive unit tests for doc-intelligence end-to-end pipeline."""

import unittest
from doc_intelligence.models import Document, DocumentMetadata
from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.ingestion.markdown_parser import MarkdownParser
from doc_intelligence.chunking.semantic_chunker import SemanticChunker
from doc_intelligence.chunking.sliding_window import SlidingWindowChunker
from doc_intelligence.retrieval.vector_store import VectorStore
from doc_intelligence.retrieval.bm25_search import BM25Retriever
from doc_intelligence.retrieval.hybrid_retriever import HybridRetriever
from doc_intelligence.evaluation.rag_evaluator import RAGEvaluator


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
