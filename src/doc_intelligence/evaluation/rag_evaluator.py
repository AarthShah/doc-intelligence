"""RAG metrics and hallucination scoring engine."""

import re
from typing import List, Set
from doc_intelligence.models import EvaluationReport


class RAGEvaluator:
    """Computes verifiable RAG evaluation scores for faithfulness and hallucination risk."""

    STOPWORDS = {
        "a", "an", "the", "and", "or", "but", "if", "in", "on", "at", "to", "for",
        "with", "is", "was", "are", "were", "be", "been", "of", "it", "this", "that"
    }

    def _extract_content_tokens(self, text: str) -> Set[str]:
        tokens = re.findall(r"\b[a-zA-Z0-9_\-]{2,}\b", text.lower())
        return {t for t in tokens if t not in self.STOPWORDS}

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
        if not answer_tokens:
            faithfulness = 1.0
        else:
            supported = answer_tokens.intersection(context_tokens)
            faithfulness = len(supported) / len(answer_tokens)

        # 2. Hallucination score: inverse of faithfulness
        hallucination = round(1.0 - faithfulness, 3)
        faithfulness = round(faithfulness, 3)

        # 3. Answer Relevance: overlap between query and answer keywords
        if not query_tokens or not answer_tokens:
            relevance = 0.0
        else:
            shared = query_tokens.intersection(answer_tokens)
            relevance = round(len(shared) / len(query_tokens), 3)

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
