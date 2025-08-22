"""
Customer related schemas - aggregating all customer data
"""
from typing import List, Optional
from decimal import Decimal
from pydantic import Field

from .base import BaseSchema
from .loan import Loan
from .card import Card
from .payment import Payment
from .credit_score import CreditScore
from .cashflow import CustomerCashflow


class CustomerBase(BaseSchema):
    """Base customer schema"""
    customer_id: str = Field(..., description="Unique customer identifier")


class CustomerProfile(CustomerBase):
    """Complete customer profile with all financial data"""
    loans: List[Loan] = Field(default_factory=list, description="Customer loans")
    cards: List[Card] = Field(default_factory=list, description="Customer credit cards")
    payments_history: List[Payment] = Field(default_factory=list, description="Payment history")
    credit_scores: List[CreditScore] = Field(default_factory=list, description="Credit score history")
    cashflow: Optional[CustomerCashflow] = Field(None, description="Cashflow information")


class CustomerSummary(CustomerBase):
    """Customer financial summary"""
    total_debt: Decimal = Field(..., description="Total outstanding debt")
    total_monthly_payments: Decimal = Field(..., description="Total monthly payment obligations")
    current_credit_score: Optional[int] = Field(None, description="Most recent credit score")
    financial_health_score: Optional[int] = Field(None, description="Overall financial health score")
    risk_level: Optional[str] = Field(None, description="Risk assessment level")
