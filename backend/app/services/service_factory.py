from fastapi import Depends

from ..db.database import MockDatabase, get_db
from .customer_service import CustomerService
from .loan_service import LoanService
from .card_service import CardService
from .payment_service import PaymentService
from .credit_score_service import CreditScoreService
from .cashflow_service import CashflowService
from .analysis_service import AnalysisService
from .azure_ai_service import AzureAIService
from .pdf_report_service import PDFReportService


# FastAPI dependency injection functions for each service
def get_customer_service(db: MockDatabase = Depends(get_db)) -> CustomerService:
    """Get customer service instance via dependency injection"""
    return CustomerService(db)


def get_loan_service(db: MockDatabase = Depends(get_db)) -> LoanService:
    """Get loan service instance via dependency injection"""
    return LoanService(db)


def get_card_service(db: MockDatabase = Depends(get_db)) -> CardService:
    """Get card service instance via dependency injection"""
    return CardService(db)


def get_payment_service(db: MockDatabase = Depends(get_db)) -> PaymentService:
    """Get payment service instance via dependency injection"""
    return PaymentService(db)


def get_credit_score_service(db: MockDatabase = Depends(get_db)) -> CreditScoreService:
    """Get credit score service instance via dependency injection"""
    return CreditScoreService(db)


def get_cashflow_service(db: MockDatabase = Depends(get_db)) -> CashflowService:
    """Get cashflow service instance via dependency injection"""
    return CashflowService(db)

def get_azure_ai_service() -> AzureAIService:
    """Get Azure AI service instance via dependency injection"""
    return AzureAIService()

def get_analysis_service(db: MockDatabase = Depends(get_db), azure_ai_service: AzureAIService = Depends(get_azure_ai_service)) -> AnalysisService:
    """Get analysis service instance via dependency injection"""
    return AnalysisService(db, azure_ai_service)

def get_pdf_report_service() -> PDFReportService:
    """Get PDF report service instance via dependency injection"""
    return PDFReportService()