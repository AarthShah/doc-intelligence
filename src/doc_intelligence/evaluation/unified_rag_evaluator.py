import json
import logging
from typing import List, Dict, Any, Optional
from doc_intelligence.evaluation.answer_relevance_evaluator import AnswerRelevanceEvaluator
from doc_intelligence.evaluation.faithfulness_evaluator import FaithfulnessEvaluator
from doc_intelligence.evaluation.hallucination_detector import HallucinationDetector

logger = logging.getLogger(__name__)

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
        logger.info(json.dumps({"event": "evaluation_started", "query": query}))

        answer_relevance_result = self.answer_relevance.evaluate(query, response)
        logger.info(json.dumps({"event": "answer_relevance_evaluated", "result": answer_relevance_result}))

        faithfulness_result = self.faithfulness.evaluate(response, context)
        logger.info(json.dumps({"event": "faithfulness_evaluated", "result": faithfulness_result}))

        hallucination_result = self.hallucination.evaluate(response, context)
        logger.info(json.dumps({"event": "hallucination_evaluated", "result": hallucination_result}))

        report = {
            "answer_relevance": answer_relevance_result,
            "faithfulness": faithfulness_result,
            "hallucination": hallucination_result,
        }

        logger.info(json.dumps({"event": "evaluation_completed", "report": report}))
        return report
