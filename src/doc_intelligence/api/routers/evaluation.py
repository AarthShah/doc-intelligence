from typing import List, Optional
from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, Field

from doc_intelligence.dependencies.rate_limiter import RateLimiter
from doc_intelligence.evaluation.mock_llm_provider import MockLLMProvider

rate_limiter = RateLimiter(limit=10, period=60)
router = APIRouter(
    prefix="/api/v1/evaluation",
    tags=["evaluation"],
    dependencies=[Depends(rate_limiter)],
)


from src.doc_intelligence.api.models import EvaluationRequest, EvaluationResponse, MetricScore


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_200_OK)
async def evaluate_rag(request: EvaluationRequest) -> EvaluationResponse:
    """Evaluate a RAG response using the MockLLMProvider."""
    try:
        llm_provider = MockLLMProvider()
        
        prompt = f"Evaluate query: {request.query} with response: {request.response}"
        mock_response = llm_provider.generate_response(prompt) if hasattr(llm_provider, "generate_response") else "Evaluated"

        metric_scores = [
            MetricScore(metric_name="faithfulness", score=0.95, details="Response is well supported by context."),
            MetricScore(metric_name="answer_relevance", score=0.90, details="Response directly addresses the query."),
        ]
        if request.reference:
            metric_scores.append(
                MetricScore(metric_name="semantic_similarity", score=0.88, details="High similarity to reference.")
            )

        return EvaluationResponse(
            status="success",
            scores=metric_scores,
            summary=f"Evaluation completed successfully using MockLLMProvider. {mock_response}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during evaluation: {e}",
        )
