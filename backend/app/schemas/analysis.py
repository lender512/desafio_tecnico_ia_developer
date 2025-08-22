"""
Financial analysis and restructuring schemas
"""
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date as Date
from pydantic import Field, validator

from .base import BaseSchema


class ConsolidationOffer(BaseSchema):
    """Schema for consolidation offer"""
    offer_id: str
    product_types_eligible: List[str]
    new_rate_pct: float = Field(..., ge=0, le=100)
    max_term_months: int = Field(..., ge=1, le=600)
    max_consolidated_balance: float = Field(..., ge=0)
    conditions: str = Field(..., description="Conditions for the offer")


class PaymentSimulationResult(BaseSchema):
    """Schema for payment simulation results"""
    months: int = Field(..., ge=0)
    total_interest: float = Field(..., ge=0)


class ConsolidationSimulationResult(BaseSchema):
    """Schema for consolidation simulation results"""
    offer_id: str
    months: int = Field(..., ge=0)
    total_interest: float = Field(..., ge=0)
    new_rate_pct: float = Field(..., ge=0, le=100)
    max_term_months: int = Field(..., ge=1, le=600)
    consolidated_amount: float = Field(..., ge=0)


class SavingsComparison(BaseSchema):
    """Schema for savings comparison between strategies"""
    interest_saved: float
    months_saved: int


class ConsolidationSavings(BaseSchema):
    """Schema for consolidation savings analysis"""
    vs_minimum: SavingsComparison
    vs_optimized: SavingsComparison


class DebtAnalysisResult(BaseSchema):
    """Schema for comprehensive debt analysis results"""
    customer_id: str
    current_credit_score: int = Field(..., ge=300, le=850)
    minimum_payment_strategy: PaymentSimulationResult
    optimized_payment_strategy: PaymentSimulationResult
    savings_vs_minimum: SavingsComparison
    consolidation_option: Optional[ConsolidationSimulationResult] = None
    consolidation_savings: Optional[ConsolidationSavings] = None
    consolidation_message: Optional[str] = None


class DebtAnalysisRequest(BaseSchema):
    """Schema for debt analysis request"""
    customer_id: str
    consolidation_offers: Optional[List[ConsolidationOffer]] = Field(default_factory=list)
    cure_dpd_first: bool = Field(default=True, description="Prioritize curing past due debts first")


class EligibleOffersRequest(BaseSchema):
    """Schema for eligible offers request"""
    customer_id: str
    offers: List[ConsolidationOffer]
    credit_score: int = Field(..., ge=300, le=850)


class EligibleOffersResponse(BaseSchema):
    """Schema for eligible offers response"""
    customer_id: str
    credit_score: int
    eligible_offers: List[ConsolidationOffer]
    total_offers_evaluated: int


class PaymentSimulationRequest(BaseSchema):
    """Schema for payment simulation request"""
    customer_id: str
    cure_dpd_first: bool = Field(default=True, description="Prioritize curing past due debts first")


class ConsolidationSimulationRequest(BaseSchema):
    """Schema for consolidation simulation request"""
    customer_id: str
    offers: List[ConsolidationOffer]
    credit_score: int = Field(..., ge=300, le=850)