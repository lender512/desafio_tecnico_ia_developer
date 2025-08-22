"""
Loan-related schemas
"""
from typing import Optional
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict

from .base import BaseSchema


class LoanBase(BaseSchema):
    """Base loan schema"""
    customer_id: str = Field(..., description="Customer ID")
    product_type: str = Field(..., description="Type of loan product")
    principal: Decimal = Field(..., ge=0, description="Principal amount")
    annual_rate_pct: Decimal = Field(..., ge=0, le=100, description="Annual interest rate percentage")
    remaining_term_months: int = Field(..., ge=0, description="Remaining term in months")
    collateral: bool = Field(..., description="Whether loan has collateral")
    days_past_due: int = Field(..., ge=0, description="Days past due")


class Loan(LoanBase):
    """Schema for loan response"""
    loan_id: str = Field(..., description="Unique loan identifier")