"""
PDF Report schemas
"""
from typing import Optional, List
from pydantic import Field

from .base import BaseSchema
from .analysis import ConsolidationOffer


class PDFReportRequest(BaseSchema):
    """Schema for PDF report generation request"""
    customer_id: str
    include_consolidation: bool = Field(default=True, description="Whether to include consolidation analysis in the report")
    consolidation_offers: Optional[List[ConsolidationOffer]] = Field(default=None, description="List of consolidation offers to include in the analysis")
    report_title: Optional[str] = Field(default=None, description="Custom title for the report")


class PDFReportResponse(BaseSchema):
    """Schema for PDF report generation response"""
    customer_id: str
    report_generated: bool
    filename: Optional[str] = None
    file_size_bytes: Optional[int] = None
    message: str
