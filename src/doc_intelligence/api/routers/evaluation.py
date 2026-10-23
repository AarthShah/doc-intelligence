from typing import List, Optional
from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/evaluation", tags=["evaluation"])


class EvaluationRequest(BaseModel):
    """Request model for RAG evaluation."""
    query: str = Field(..., description="The user query.")
    response: str = Field(..., description="The generated RAG response.")
    retrieved_contexts: List[str] = Field(default_factory=list, description="The contexts retrieved for the query.")
    reference: Optional[str] = Field(None, description="Optional ground truth reference answer.")


class MetricScore(BaseModel):
    """Score for an individual evaluation metric."""
    metric_name: str
    score: float
    details: Optional[str] = None


class EvaluationResponse(BaseModel):
    """Response model for RAG evaluation."""
    status: str = "success"
    scores: List[MetricScore] = Field(default_factory=list)
    summary: Optional[str] = None


@router.post("", response_model=EvaluationResponse, status_code=status.HTTP_200_OK)
async def evaluate_rag(request: EvaluationRequest) -> EvaluationResponse:
    """Evaluate a RAG response using a mock evaluator."""
    try:
        # Mock evaluation logic
        mock_scores = [
            MetricScore(metric_name="faithfulness", score=0.95, details="Response is well supported by context."),
            MetricScore(metric_name="answer_relevance", score=0.90, details="Response directly addresses the query."),
        ]
        if request.reference:
            mock_scores.append(
                MetricScore(metric_name="semantic_similarity", score=0.88, details="High similarity to reference.")
            )

        return EvaluationResponse(
            status="success",
            scores=mock_scores,
            summary="Evaluation completed successfully using mock evaluator.",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred during evaluation: {e}",
        )
