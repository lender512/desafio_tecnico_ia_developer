"""
Credit card related schemas
"""
from typing import Optional
from decimal import Decimal
from pydantic import Field

from .base import BaseSchema


class CardBase(BaseSchema):
    """Base credit card schema"""
    customer_id: str = Field(..., description="Customer ID")
    balance: Decimal = Field(..., ge=0, description="Current balance")
    annual_rate_pct: Decimal = Field(..., ge=0, le=100, description="Annual interest rate percentage")
    min_payment_pct: Decimal = Field(..., ge=0, le=100, description="Minimum payment percentage")
    payment_due_day: int = Field(..., ge=1, le=31, description="Payment due day of the month")
    days_past_due: int = Field(..., ge=0, description="Days past due")



class Card(CardBase):
    """Schema for credit card response"""
    card_id: str = Field(..., description="Unique card identifier")
