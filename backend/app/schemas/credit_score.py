"""
Credit score related schemas
"""
from typing import Optional
from datetime import date as Date
from pydantic import Field

from .base import BaseSchema


class CreditScoreBase(BaseSchema):
    """Base credit score schema"""
    customer_id: str = Field(..., description="Customer ID")
    date: Date = Field(..., description="Score date")
    credit_score: int = Field(..., ge=300, le=850, description="Credit score (300-850)")


class CreditScore(CreditScoreBase):
    """Schema for credit score response"""
    score_id: Optional[str] = Field(None, description="Unique score identifier")
