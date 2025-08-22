from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.credit_score_service import CreditScoreService
from app.schemas.credit_score import CreditScore
from app.schemas.base import SuccessResponse

router = APIRouter()


@router.get("/credit-scores", response_model=SuccessResponse[List[CreditScore]])
async def get_all_credit_scores(
    credit_service: CreditScoreService = Depends()
):
    """Get all credit scores in the system"""
    return SuccessResponse(message="All credit scores retrieved successfully", data=credit_service.get_all_credit_scores())


@router.get("/customers/{customer_id}/credit-scores", response_model=SuccessResponse[List[CreditScore]])
async def get_credit_scores_by_customer(
    customer_id: str,
    credit_service: CreditScoreService = Depends()
):
    """Get all credit scores for a specific customer"""
    return SuccessResponse(message="Customer credit scores retrieved successfully", data=credit_service.get_credit_scores_by_customer(customer_id))


@router.get("/customers/{customer_id}/credit-score/current", response_model=SuccessResponse[CreditScore])
async def get_current_credit_score(
    customer_id: str,
    credit_service: CreditScoreService = Depends()
):
    """Get the most recent credit score for a customer"""
    score = credit_service.get_current_credit_score(customer_id)
    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No credit score found for customer {customer_id}"
        )
    return SuccessResponse(message="Current credit score retrieved successfully", data=score)
