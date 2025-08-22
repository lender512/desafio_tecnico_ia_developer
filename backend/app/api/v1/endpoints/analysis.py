from fastapi import APIRouter, Depends, HTTPException
from typing import List

from app.services.service_factory import get_analysis_service
from app.services.analysis_service import AnalysisService
from app.schemas.base import SuccessResponse
from app.schemas.analysis import (
    DebtAnalysisResult,
    DebtAnalysisRequest,
    PaymentSimulationResult,
    PaymentSimulationRequest,
    ConsolidationSimulationRequest,
    ConsolidationSimulationResult,
    EligibleOffersRequest,
    EligibleOffersResponse
)

router = APIRouter()


@router.post("/analysis/debt-analysis", response_model=SuccessResponse[DebtAnalysisResult])
async def analyze_customer_debt(
    request: DebtAnalysisRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Comprehensive debt analysis for a customer including minimum payments, 
    optimized payments, and consolidation options
    """
    try:
        result = analysis_service.analyze_customer_debt(
            customer_id=request.customer_id,
            consolidation_offers=request.consolidation_offers
        )
        return SuccessResponse(message="Debt analysis completed successfully", data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.post("/analysis/simulate-minimum-payments", response_model=SuccessResponse[PaymentSimulationResult])
async def simulate_minimum_payments(
    request: PaymentSimulationRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Simulate minimum payment strategy for a customer
    """
    try:
        result = analysis_service.simulate_minimum_payments(request.customer_id)
        return SuccessResponse(message="Minimum payment simulation completed successfully", data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/analysis/simulate-optimized-payments", response_model=SuccessResponse[PaymentSimulationResult])
async def simulate_optimized_payments(
    request: PaymentSimulationRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Simulate optimized payment strategy (avalanche method) for a customer
    """
    try:
        result = analysis_service.simulate_optimized_payments(
            customer_id=request.customer_id,
            cure_dpd_first=request.cure_dpd_first
        )
        return SuccessResponse(message="Optimized payment simulation completed successfully", data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.post("/analysis/simulate-consolidation", response_model=SuccessResponse[ConsolidationSimulationResult])
async def simulate_consolidation(
    request: ConsolidationSimulationRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Simulate debt consolidation for a customer
    """
    try:
        result = analysis_service.simulate_consolidation(
            customer_id=request.customer_id,
            offers=request.offers,
            credit_score=request.credit_score
        )
        if result is None:
            raise HTTPException(status_code=404, detail="No eligible consolidation offers available")
        return SuccessResponse(message="Consolidation simulation completed successfully", data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Consolidation simulation failed: {str(e)}")


@router.post("/analysis/eligible-offers", response_model=SuccessResponse[EligibleOffersResponse])
async def get_eligible_offers(
    request: EligibleOffersRequest,
    analysis_service: AnalysisService = Depends(get_analysis_service)
):
    """
    Get eligible consolidation offers for a customer based on their current debts and credit score
    """
    try:
        result = analysis_service.get_eligible_offers(
            customer_id=request.customer_id,
            offers=request.offers,
            credit_score=request.credit_score
        )
        return SuccessResponse(message="Eligible offers retrieved successfully", data=result)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Offer evaluation failed: {str(e)}")
