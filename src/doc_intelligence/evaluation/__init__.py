"""Evaluation subsystem: Verifiable RAG metrics and hallucination scoring."""

from doc_intelligence.evaluation.answer_relevance_evaluator import AnswerRelevanceEvaluator
from doc_intelligence.evaluation.faithfulness_evaluator import FaithfulnessEvaluator
from doc_intelligence.evaluation.hallucination_detector import HallucinationDetector
from doc_intelligence.evaluation.mock_llm_provider import MockLLMProvider
from doc_intelligence.evaluation.rag_evaluator import RAGEvaluator
from doc_intelligence.evaluation.unified_rag_evaluator import UnifiedRAGEvaluator

__all__ = ["RAGEvaluator", "UnifiedRAGEvaluator", "FaithfulnessEvaluator", "AnswerRelevanceEvaluator", "HallucinationDetector", "MockLLMProvider"]
