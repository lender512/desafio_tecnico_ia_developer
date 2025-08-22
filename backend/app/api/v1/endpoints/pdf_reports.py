"""
PDF Report endpoints
"""
import os
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import FileResponse

from app.db.database import MockDatabase, get_db
from app.schemas.pdf_report import PDFReportRequest, PDFReportResponse
from app.schemas.analysis import ConsolidationOffer
from app.services.service_factory import get_pdf_report_service, get_analysis_service, get_azure_ai_service
from app.services.pdf_report_service import PDFReportService
from app.services.analysis_service import AnalysisService
from app.services.azure_ai_service import AzureAIService

router = APIRouter()


@router.post("/generate-report", response_model=PDFReportResponse)
async def generate_pdf_report(
    request: PDFReportRequest,
    db: MockDatabase = Depends(get_db),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    pdf_service: PDFReportService = Depends(get_pdf_report_service)
):
    """
    Generate a comprehensive PDF financial report for a customer
    """
    try:
        # Check if customer exists
        customer_data = db.get_customer_data(request.customer_id)
        if not customer_data:
            raise HTTPException(status_code=404, detail=f"Customer {request.customer_id} not found")
        
        # Prepare consolidation offers if requested
        consolidation_offers = []
        if request.include_consolidation and request.consolidation_offers:
            consolidation_offers = request.consolidation_offers

        # Perform debt analysis
        analysis_result = analysis_service.analyze_customer_debt(
            customer_id=request.customer_id,
            consolidation_offers=consolidation_offers
        )
        
        # Generate PDF report
        pdf_bytes = pdf_service.generate_financial_report(analysis_result)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"financial_report_{request.customer_id}_{timestamp}.pdf"
        
        # Save to temporary file for file response
        temp_path = f"/tmp/{filename}"
        with open(temp_path, 'wb') as f:
            f.write(pdf_bytes)
        
        return PDFReportResponse(
            customer_id=request.customer_id,
            report_generated=True,
            filename=filename,
            file_size_bytes=len(pdf_bytes),
            message="PDF report generated successfully"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")


@router.get("/download-report/{customer_id}/{filename}")
async def download_pdf_report(customer_id: str, filename: str):
    """
    Download a generated PDF report
    """
    try:
        file_path = f"/tmp/{filename}"
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Report file not found")
        
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error downloading report: {str(e)}")


@router.post("/generate-and-download")
async def generate_and_download_report(
    request: PDFReportRequest,
    db: MockDatabase = Depends(get_db),
    azure_ai_service: AzureAIService = Depends(get_azure_ai_service),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    pdf_service: PDFReportService = Depends(get_pdf_report_service)
):
    """
    Generate and immediately download a PDF financial report
    """
    try:
        # Check if customer exists
        customer_data = db.get_customer_data(request.customer_id)
        if not customer_data:
            raise HTTPException(status_code=404, detail=f"Customer {request.customer_id} not found")
        
        # Prepare consolidation offers if requested
        consolidation_offers = []
        if request.include_consolidation and request.consolidation_offers:
            consolidation_offers = request.consolidation_offers

        # Perform debt analysis
        analysis_result = analysis_service.analyze_customer_debt(
            customer_id=request.customer_id,
            consolidation_offers=consolidation_offers
        )
        
        # Generate PDF report
        pdf_bytes = pdf_service.generate_financial_report(analysis_result)
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"financial_report_{request.report_title}_{request.customer_id}_{timestamp}.pdf"
        
        # Return PDF as response
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating report: {str(e)}")
