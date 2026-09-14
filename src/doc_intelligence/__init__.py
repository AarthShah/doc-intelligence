"""doc-intelligence: Autonomous Document Intelligence & RAG Evaluation Platform."""

__version__ = "0.1.0"
__author__ = "Aarth Shah"

from doc_intelligence.models import Document, Chunk, QueryResult, EvaluationReport
from doc_intelligence.ingestion.text_parser import TextParser
from doc_intelligence.chunking.semantic_chunker import SemanticChunker
from doc_intelligence.retrieval.hybrid_retriever import HybridRetriever
from doc_intelligence.evaluation.rag_evaluator import RAGEvaluator

__all__ = [
    "Document",
    "Chunk",
    "QueryResult",
    "EvaluationReport",
    "TextParser",
    "SemanticChunker",
    "HybridRetriever",
    "RAGEvaluator",
]
