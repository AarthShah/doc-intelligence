"""Evaluation subsystem: Verifiable RAG metrics and hallucination scoring."""

from doc_intelligence.evaluation.faithfulness_evaluator import FaithfulnessEvaluator
from doc_intelligence.evaluation.rag_evaluator import RAGEvaluator

__all__ = ["RAGEvaluator", "FaithfulnessEvaluator"]
