"""
Customer cashflow related schemas
"""
from typing import Optional
from decimal import Decimal
from pydantic import Field

from .base import BaseSchema


class CustomerCashflowBase(BaseSchema):
    """Base customer cashflow schema"""
    customer_id: str = Field(..., description="Customer ID")
    monthly_income_avg: Decimal = Field(..., ge=0, description="Average monthly income")
    income_variability_pct: Decimal = Field(..., ge=0, le=100, description="Income variability percentage")
    essential_expenses_avg: Decimal = Field(..., ge=0, description="Average essential expenses")



class CustomerCashflow(CustomerCashflowBase):
    """Schema for customer cashflow response"""
    cashflow_id: Optional[str] = Field(None, description="Unique cashflow identifier")
