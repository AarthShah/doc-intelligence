from unittest.mock import MagicMock, patch
import pytest

from doc_intelligence.evaluation.rag_evaluator import UnifiedRAGEvaluator


def test_unified_rag_evaluator_run_evaluation():
    with patch("doc_intelligence.evaluation.rag_evaluator.FaithfulnessEvaluator") as mock_faithfulness_cls, \
         patch("doc_intelligence.evaluation.rag_evaluator.AnswerRelevanceEvaluator") as mock_relevance_cls, \
         patch("doc_intelligence.evaluation.rag_evaluator.HallucinationDetector") as mock_hallucination_cls:

        mock_faithfulness_instance = mock_faithfulness_cls.return_value
        mock_faithfulness_instance.evaluate.return_value = {"faithfulness_score": 0.95}

        mock_relevance_instance = mock_relevance_cls.return_value
        mock_relevance_instance.evaluate.return_value = {"answer_relevance_score": 0.88}

        mock_hallucination_instance = mock_hallucination_cls.return_value
        mock_hallucination_instance.detect.return_value = {"is_hallucination": False, "score": 0.05}

        evaluator = UnifiedRAGEvaluator(
            faithfulness_evaluator=mock_faithfulness_instance,
            answer_relevance_evaluator=mock_relevance_instance,
            hallucination_detector=mock_hallucination_instance,
        )

        query = "What is doc-intelligence?"
        contexts = ["Doc-intelligence is an enterprise-grade platform."]
        answer = "Doc-intelligence is a platform for document ingestion and evaluation."

        report = evaluator.run_evaluation(query=query, contexts=contexts, answer=answer)

        mock_faithfulness_instance.evaluate.assert_called_once_with(contexts, answer)
        mock_relevance_instance.evaluate.assert_called_once_with(query, answer)
        mock_hallucination_instance.detect.assert_called_once_with(contexts[0], answer)

        assert isinstance(report, dict)
        assert report.get("faithfulness") == {"faithfulness_score": 0.95}
        assert report.get("answer_relevance") == {"answer_relevance_score": 0.88}
        assert report.get("hallucination") == {"is_hallucination": False, "score": 0.05}
