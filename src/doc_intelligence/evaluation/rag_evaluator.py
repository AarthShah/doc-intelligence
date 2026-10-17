"""RAG metrics and hallucination scoring engine."""

import re
from typing import List, Set
from doc_intelligence.models import EvaluationReport
from doc_intelligence.evaluation.faithfulness_evaluator import FaithfulnessEvaluator
from doc_intelligence.evaluation.answer_relevance_evaluator import AnswerRelevanceEvaluator
from doc_intelligence.evaluation.hallucination_detector import HallucinationDetector


class RAGEvaluator:
    """Computes verifiable RAG evaluation scores for faithfulness and hallucination risk."""

    def __init__(
        self,
        faithfulness_evaluator: FaithfulnessEvaluator = None,
        answer_relevance_evaluator: AnswerRelevanceEvaluator = None,
        hallucination_detector: HallucinationDetector = None,
    ):
        self.faithfulness_evaluator = faithfulness_evaluator
        self.answer_relevance_evaluator = answer_relevance_evaluator
        self.hallucination_detector = hallucination_detector

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
            res = self.faithfulness_evaluator.evaluate(context, answer)
            if isinstance(res, dict):
                return res.get("faithfulness_score", 0.0)
            return float(res)

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
        faithfulness_result = self.evaluate_faithfulness(context, answer, answer_tokens, context_tokens)
        if isinstance(faithfulness_result, dict):
            faithfulness_score = faithfulness_result.get("faithfulness_score", 0.0)
        else:
            faithfulness_score = float(faithfulness_result)
        
        faithfulness = round(faithfulness_score, 3)

        # 2. Hallucination score: use hallucination detector if available, else inverse of faithfulness
        if self.hallucination_detector:
            det_result = self.hallucination_detector.detect(context_text, answer)
            if isinstance(det_result, dict):
                h_score = det_result.get("hallucination_score")
                if h_score is None and "score" in det_result:
                    h_score = det_result.get("score")
                if h_score is None:
                    h_score = 1.0 - faithfulness_score
                hallucination = round(float(h_score), 3)
            else:
                hallucination = round(1.0 - faithfulness_score, 3)
        else:
            hallucination = round(1.0 - faithfulness_score, 3)

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


class UnifiedRAGEvaluator:
    """
    Orchestrates the execution of individual RAG evaluation metrics.

    This class aggregates scores from faithfulness, answer relevance, and hallucination
    detection into a single, comprehensive evaluation report.
    """

    def __init__(
        self,
        faithfulness_evaluator: FaithfulnessEvaluator = None,
        answer_relevance_evaluator: AnswerRelevanceEvaluator = None,
        hallucination_detector: HallucinationDetector = None,
    ):
        """
        Initializes the UnifiedRAGEvaluator with optional evaluators.

        Args:
            faithfulness_evaluator: An instance of FaithfulnessEvaluator.
            answer_relevance_evaluator: An instance of AnswerRelevanceEvaluator.
            hallucination_detector: An instance of HallucinationDetector.
        """
        self.faithfulness_evaluator = faithfulness_evaluator
        self.answer_relevance_evaluator = answer_relevance_evaluator
        self.hallucination_detector = hallucination_detector
        self.rag_evaluator = RAGEvaluator(
            faithfulness_evaluator=self.faithfulness_evaluator,
            answer_relevance_evaluator=self.answer_relevance_evaluator,
            hallucination_detector=self.hallucination_detector,
        )

    def run_evaluation(
        self,
        query: str,
        contexts: List[str],
        answer: str,
        ground_truth: str = "",
    ) -> dict:
        """
        Runs all configured RAG evaluation metrics.

        Args:
            query: The user's query/question.
            contexts: A list of strings representing the retrieved context documents.
            answer: The generated answer.
            ground_truth: Optional expected correct answer.

        Returns:
            A dictionary containing the evaluation scores and details.
        """
        evaluation_report = self.rag_evaluator.evaluate(
            query=query,
            context=contexts,
            answer=answer,
            ground_truth=ground_truth,
        )

        ans_rel_score = evaluation_report.answer_relevance_score
        if isinstance(ans_rel_score, dict):
            ans_rel_dict = ans_rel_score
            ans_rel_val = ans_rel_dict.get("answer_relevance_score", 0.0)
        else:
            ans_rel_val = float(ans_rel_score)
            ans_rel_dict = {"answer_relevance_score": ans_rel_val}

        faithfulness_score = evaluation_report.faithfulness_score
        if isinstance(faithfulness_score, dict):
            faithfulness_dict = faithfulness_score
            faithfulness_val = faithfulness_dict.get("faithfulness_score", 0.0)
        else:
            faithfulness_val = float(faithfulness_score)
            faithfulness_dict = {"faithfulness_score": faithfulness_val}

        return {
            "faithfulness": faithfulness_dict,
            "answer_relevance": ans_rel_dict,
            "hallucination": {
                "score": evaluation_report.hallucination_score,
                "is_hallucination": evaluation_report.hallucination_score > 0.5,
            },
            "faithfulness_score": faithfulness_val,
            "answer_relevance_score": ans_rel_val,
            "context_recall_score": evaluation_report.context_recall_score,
            "hallucination_score": evaluation_report.hallucination_score,
        }
