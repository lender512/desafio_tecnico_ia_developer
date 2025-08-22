from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.loan_service import LoanService
from app.schemas.loan import Loan
from app.schemas.base import SuccessResponse

router = APIRouter()


@router.get("/loans", response_model=SuccessResponse[List[Loan]])
async def get_all_loans(
    loan_service: LoanService = Depends()
):
    """Get all loans in the system"""
    return SuccessResponse(message="All loans retrieved successfully", data=loan_service.get_all_loans())


@router.get("/loans/{loan_id}", response_model=SuccessResponse[Loan])
async def get_loan_by_id(
    loan_id: str,
    loan_service: LoanService = Depends()
):
    """Get a specific loan by ID"""
    loan = loan_service.get_loan_by_id(loan_id)
    if not loan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Loan {loan_id} not found"
        )
    return SuccessResponse(message="Loan retrieved successfully", data=loan)


@router.get("/customers/{customer_id}/loans", response_model=SuccessResponse[List[Loan]])
async def get_loans_by_customer(
    customer_id: str,
    loan_service: LoanService = Depends()
):
    """Get all loans for a specific customer"""
    return SuccessResponse(message="Customer loans retrieved successfully", data=loan_service.get_loans_by_customer(customer_id))
