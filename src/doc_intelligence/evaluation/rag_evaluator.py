"""RAG metrics and hallucination scoring engine."""

import re
from typing import List, Set
from doc_intelligence.models import EvaluationReport
from doc_intelligence.evaluation.faithfulness_evaluator import FaithfulnessEvaluator
from doc_intelligence.evaluation.answer_relevance_evaluator import AnswerRelevanceEvaluator


class RAGEvaluator:
    """Computes verifiable RAG evaluation scores for faithfulness and hallucination risk."""

    def __init__(
        self,
        faithfulness_evaluator: FaithfulnessEvaluator = None,
        answer_relevance_evaluator: AnswerRelevanceEvaluator = None,
    ):
        self.faithfulness_evaluator = faithfulness_evaluator
        self.answer_relevance_evaluator = answer_relevance_evaluator

    STOPWORDS = {
        "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "for",
        "with", "is", "was", "are", "were", "be", "been", "of", "it", "this", "that"
    }

    def _extract_content_tokens(self, text: str) -> Set[str]:
        tokens = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())
        return {t for t in tokens if t not in self.STOPWORDS}

    def evaluate_faithfulness(
        self,
        context: List[str],
        answer: str,
        answer_tokens: Set[str] = None,
        context_tokens: Set[str] = None,
    ) -> float:
        """Score the faithfulness of generated answers against context."""
        if self.faithfulness_evaluator:
            return self.faithfulness_evaluator.evaluate(context, answer)

        if answer_tokens is None:
            answer_tokens = self._extract_content_tokens(answer)
        if context_tokens is None:
            context_text = " ".join(context)
            context_tokens = self._extract_content_tokens(context_text)

        if not answer_tokens:
            return 1.0
        supported = answer_tokens.intersection(context_tokens)
        return len(supported) / len(answer_tokens)

    def evaluate_answer_relevance(
        self,
        query: str,
        answer: str,
        query_tokens: Set[str] = None,
        answer_tokens: Set[str] = None,
    ) -> float:
        """Score the relevance of generated answers against user queries."""
        if self.answer_relevance_evaluator:
            return self.answer_relevance_evaluator.evaluate(query, answer)

        if query_tokens is None:
            query_tokens = self._extract_content_tokens(query)
        if answer_tokens is None:
            answer_tokens = self._extract_content_tokens(answer)

        if not query_tokens or not answer_tokens:
            return 0.0
        shared = query_tokens.intersection(answer_tokens)
        return round(len(shared) / len(query_tokens), 3)

    def evaluate(
        self,
        query: str,
        context: List[str],
        answer: str,
        ground_truth: str = "",
    ) -> EvaluationReport:
        """Calculate Faithfulness, Answer Relevance, Context Recall, and Hallucination Score."""
        query_tokens = self._extract_content_tokens(query)
        answer_tokens = self._extract_content_tokens(answer)
        context_text = " ".join(context)
        context_tokens = self._extract_content_tokens(context_text)

        # 1. Faithfulness: what proportion of answer content tokens appear in the context
        faithfulness = self.evaluate_faithfulness(context, answer, answer_tokens, context_tokens)

        # 2. Hallucination score: inverse of faithfulness
        hallucination = round(1.0 - faithfulness, 3)
        faithfulness = round(faithfulness, 3)

        # 3. Answer Relevance: overlap between query and answer keywords
        relevance = self.evaluate_answer_relevance(query, answer, query_tokens, answer_tokens)

        # 4. Context Recall (if ground truth provided)
        if ground_truth:
            gt_tokens = self._extract_content_tokens(ground_truth)
            if gt_tokens:
                recalled = gt_tokens.intersection(context_tokens)
                recall = round(len(recalled) / len(gt_tokens), 3)
            else:
                recall = 1.0
        else:
            # Fallback: context overlap with query
            recall = round(len(query_tokens.intersection(context_tokens)) / max(1, len(query_tokens)), 3)

        return EvaluationReport(
            query=query,
            answer=answer,
            faithfulness_score=faithfulness,
            answer_relevance_score=relevance,
            context_recall_score=recall,
            hallucination_score=hallucination,
            details={
                "unsupported_answer_tokens": list(answer_tokens - context_tokens)[:10],
                "grounded_tokens_count": len(answer_tokens.intersection(context_tokens)),
                "total_answer_tokens": len(answer_tokens),
            },
        )
