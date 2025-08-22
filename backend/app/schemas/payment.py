"""
Payment related schemas
"""
from typing import Optional, Literal
from decimal import Decimal
from datetime import date as Date
from pydantic import Field

from .base import BaseSchema


class PaymentBase(BaseSchema):
    """Base payment schema"""
    product_id: str = Field(..., description="Product ID (loan or card)")
    product_type: Literal["loan", "card"] = Field(..., description="Type of product")
    customer_id: str = Field(..., description="Customer ID")
    date: Date = Field(..., description="Payment date")
    amount: Decimal = Field(..., ge=0, description="Payment amount")



class Payment(PaymentBase):
    """Schema for payment response"""
    payment_id: Optional[str] = Field(None, description="Unique payment identifier")
