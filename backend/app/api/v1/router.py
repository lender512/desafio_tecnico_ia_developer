from fastapi import APIRouter

from app.api.v1.endpoints import (
    health, 
    customers, 
    loans, 
    cards, 
    payments, 
    credit_scores, 
    cashflows,
    analysis,
    pdf_reports
)

api_router = APIRouter()

api_router.include_router(health.router, tags=["health"])
api_router.include_router(customers.router, tags=["customers"])
api_router.include_router(loans.router, tags=["loans"])
api_router.include_router(cards.router, tags=["cards"])
api_router.include_router(payments.router, tags=["payments"])
api_router.include_router(credit_scores.router, tags=["credit-scores"])
api_router.include_router(cashflows.router, tags=["cashflows"])
api_router.include_router(analysis.router, tags=["analysis"])
api_router.include_router(pdf_reports.router, prefix="/reports", tags=["pdf-reports"])
