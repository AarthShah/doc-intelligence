from typing import List, Dict, Any
from doc_intelligence.evaluation.answer_relevance_evaluator import AnswerRelevanceEvaluator
from doc_intelligence.evaluation.faithfulness_evaluator import FaithfulnessEvaluator
from doc_intelligence.evaluation.hallucination_detector import HallucinationDetector

class UnifiedRAGEvaluator:
    """
    Orchestrates all evaluation metrics into a single runner that outputs detailed JSON reports.
    """

    def __init__(self):
        self.answer_relevance = AnswerRelevanceEvaluator()
        self.faithfulness = FaithfulnessEvaluator()
        self.hallucination = HallucinationDetector()

    def evaluate(self, query: str, response: str, context: List[str]) -> Dict[str, Any]:
        """
        Runs all evaluation metrics and returns a consolidated report.
        """
        return {
            "answer_relevance": self.answer_relevance.evaluate(query, response),
            "faithfulness": self.faithfulness.evaluate(response, context),
            "hallucination": self.hallucination.evaluate(response, context),
        }
