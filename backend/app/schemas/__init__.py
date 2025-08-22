"""
Pydantic schemas for request/response models
"""

# Base schemas
from .base import (
    BaseSchema,
    HealthResponse,
    MessageResponse,
    ErrorResponse,
    SuccessResponse
)

# Financial product schemas
from .loan import (
    LoanBase,
    Loan,
)

from .card import (
    CardBase,
    Card,
)

from .payment import (
    PaymentBase,
    Payment,
)

from .credit_score import (
    CreditScoreBase,
    CreditScore,
)

from .cashflow import (
    CustomerCashflowBase,
    CustomerCashflow,
)

# Customer schemas
from .customer import (
    CustomerBase,
    CustomerProfile,
    CustomerSummary,
)

# Analysis schemas
# from .analysis import (
    
# )

__all__ = [
    # Base
    "BaseSchema",
    "HealthResponse",
    "MessageResponse", 
    "ErrorResponse",
    "SuccessResponse",
    
    # Loan
    "LoanBase",
    "Loan",
    
    # Card
    "CardBase",
    "Card",
    
    # Payment
    "PaymentBase",
    "Payment",
    
    # Credit Score
    "CreditScoreBase",
    "CreditScore",
    
    # Cashflow
    "CustomerCashflowBase",
    "CustomerCashflow",
    
    # Customer
    "CustomerBase",
    "CustomerProfile",
    "CustomerSummary",
    
    # Analysis
]
