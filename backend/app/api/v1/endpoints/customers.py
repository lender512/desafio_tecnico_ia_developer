from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.customer_service import CustomerService
from app.schemas.customer import CustomerProfile, CustomerSummary
from app.schemas.base import SuccessResponse, MessageResponse

router = APIRouter()


@router.get("/customers", response_model=SuccessResponse[List[str]])
async def list_customers(
    customer_service: CustomerService = Depends()
):
    """Get list of all customer IDs"""
    return SuccessResponse(message="All customer IDs retrieved successfully", data=customer_service.list_all_customers())


@router.get("/customers/{customer_id}/profile", response_model=SuccessResponse[CustomerProfile])
async def get_customer_profile(
    customer_id: str,
    customer_service: CustomerService = Depends()
):
    """Get complete customer profile with all financial data"""
    profile = customer_service.get_customer_profile(customer_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found"
        )
    return SuccessResponse(message="Customer profile retrieved successfully", data=profile)


@router.get("/customers/{customer_id}/summary", response_model=SuccessResponse[CustomerSummary])
async def get_customer_summary(
    customer_id: str,
    customer_service: CustomerService = Depends()
):
    """Get customer financial summary"""
    summary = customer_service.get_customer_summary(customer_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Customer {customer_id} not found"
        )
    return SuccessResponse(message="Customer summary retrieved successfully", data=summary)


@router.get("/customers/{customer_id}/exists", response_model=SuccessResponse[dict])
async def check_customer_exists(
    customer_id: str,
    customer_service: CustomerService = Depends()
):
    """Check if customer exists in the system"""
    exists = customer_service.customer_exists(customer_id)
    return SuccessResponse(
        message="Customer existence check completed",
        data={"customer_id": customer_id, "exists": exists}
    )
