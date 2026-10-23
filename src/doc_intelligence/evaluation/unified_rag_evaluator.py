from typing import List, Dict, Any, Optional
from doc_intelligence.evaluation.answer_relevance_evaluator import AnswerRelevanceEvaluator
from doc_intelligence.evaluation.faithfulness_evaluator import FaithfulnessEvaluator
from doc_intelligence.evaluation.hallucination_detector import HallucinationDetector

class UnifiedRAGEvaluator:
    """
    Orchestrates all evaluation metrics into a single runner that outputs detailed JSON reports.
    """

    def __init__(
        self,
        llm_provider: Optional[Any] = None,
        answer_relevance_evaluator: Optional[Any] = None,
        faithfulness_evaluator: Optional[Any] = None,
        hallucination_detector: Optional[Any] = None,
    ):
        self.answer_relevance = answer_relevance_evaluator or AnswerRelevanceEvaluator(llm_provider=llm_provider)
        self.faithfulness = faithfulness_evaluator or FaithfulnessEvaluator(llm_provider=llm_provider)
        self.hallucination = hallucination_detector or HallucinationDetector(llm_provider=llm_provider)

    def evaluate(self, query: str, response: str, context: List[str]) -> Dict[str, Any]:
        """
        Runs all evaluation metrics and returns a consolidated report.
        """
        return {
            "answer_relevance": self.answer_relevance.evaluate(query, response),
            "faithfulness": self.faithfulness.evaluate(response, context),
            "hallucination": self.hallucination.evaluate(response, context),
        }
