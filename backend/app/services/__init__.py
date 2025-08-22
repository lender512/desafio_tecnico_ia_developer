"""
Services package for the application.
All services are read-only and provide access to preloaded data.
"""

from .customer_service import CustomerService
from .loan_service import LoanService
from .card_service import CardService
from .payment_service import PaymentService
from .credit_score_service import CreditScoreService
from .cashflow_service import CashflowService
from .analysis_service import AnalysisService
from .azure_ai_service import AzureAIService

__all__ = [
    "CustomerService",
    "LoanService", 
    "CardService",
    "PaymentService",
    "CreditScoreService",
    "CashflowService",
    "AnalysisService",
    "AzureAIService",
]
