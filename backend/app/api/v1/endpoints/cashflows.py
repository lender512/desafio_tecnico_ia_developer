from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.cashflow_service import CashflowService
from app.schemas.cashflow import CustomerCashflow
from app.schemas.base import SuccessResponse

router = APIRouter()


@router.get("/cashflows", response_model=SuccessResponse[List[CustomerCashflow]])
async def get_all_cashflows(
    cashflow_service: CashflowService = Depends()
):
    """Get all customer cashflow records"""
    return SuccessResponse(message="All cashflows retrieved successfully", data=cashflow_service.get_all_cashflows())


@router.get("/customers/{customer_id}/cashflow", response_model=SuccessResponse[CustomerCashflow])
async def get_customer_cashflow(
    customer_id: str,
    cashflow_service: CashflowService = Depends()
):
    """Get cashflow information for a specific customer"""
    cashflow = cashflow_service.get_customer_cashflow(customer_id)
    if not cashflow:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No cashflow data found for customer {customer_id}"
        )
    return SuccessResponse(message="Customer cashflow retrieved successfully", data=cashflow)
