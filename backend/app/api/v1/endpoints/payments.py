from typing import List
from fastapi import APIRouter, Depends

from app.services.payment_service import PaymentService
from app.schemas.payment import Payment
from app.schemas.base import SuccessResponse

router = APIRouter()


@router.get("/payments", response_model=SuccessResponse[List[Payment]])
async def get_all_payments(
    payment_service: PaymentService = Depends()
):
    """Get all payments in the system"""
    return SuccessResponse(message="All payments retrieved successfully", data=payment_service.get_all_payments())


@router.get("/customers/{customer_id}/payments", response_model=SuccessResponse[List[Payment]])
async def get_payments_by_customer(
    customer_id: str,
    payment_service: PaymentService = Depends()
):
    """Get all payments for a specific customer"""
    return SuccessResponse(message="Customer payments retrieved successfully", data=payment_service.get_payments_by_customer(customer_id))


@router.get("/products/{product_id}/payments", response_model=SuccessResponse[List[Payment]])
async def get_payments_by_product(
    product_id: str,
    payment_service: PaymentService = Depends()
):
    """Get all payments for a specific product (loan or card)"""
    return SuccessResponse(message="Product payments retrieved successfully", data=payment_service.get_payments_by_product(product_id))
