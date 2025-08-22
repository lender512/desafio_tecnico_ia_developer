"""
PDF Report schemas for generation, document structure, and API responses.
"""
from typing import Optional, List, Dict, Any, TypedDict
from pydantic import BaseModel, Field

from .base import BaseSchema
from .analysis import ConsolidationOffer, DebtAnalysisResult


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


class MarkdownDoc(BaseModel):
    """Schema for structured markdown document generation."""
    title: str = Field(description="Top-level report title (Markdown H1 text, no leading #).")
    report_date: str = Field(description="Human-readable date, e.g., 'August 22, 2025'.")
    customer_id: str
    credit_score: int
    executive_summary: str
    payment_strategy_analysis: str
    financial_comparison_table_markdown: str = Field(
        description="A Markdown table comparing strategies. Must be valid GitHub-flavored Markdown table."
    )
    consolidation_analysis: Optional[str] = None
    savings_analysis: str
    recommendations: List[str] = Field(description="Bullet points (without leading dashes).")
    markdown: Optional[str] = Field(
        default=None,
        description="(Optional) Full, ready-to-render Markdown for the entire report."
    )


class HtmlConversion(BaseModel):
    """Structured response for Markdown -> HTML conversion."""
    html: str = Field(description="Clean semantic HTML fragment WITHOUT doctype/html/head/body wrappers.")
    heading_levels: List[int] = Field(
        default_factory=list,
        description="List of heading levels used (e.g., [1,2,3] if h1/h2/h3 appear)."
    )
    had_tables: bool = Field(
        default=False,
        description="True if at least one Markdown table was converted."
    )
    warnings: Optional[List[str]] = Field(
        default=None,
        description="Any non-fatal conversion warnings (e.g., malformed table rows)."
    )


class ReportState(TypedDict):
    """State for the LangGraph workflow in PDF report generation."""
    analysis_data: DebtAnalysisResult
    raw_analysis: str
    markdown_content: str
    styled_html: str
    pdf_bytes: bytes


class ReportContext(BaseModel):
    """Context data prepared for report generation."""
    consolidation: str
    customer_summary: Dict[str, Any]
    payment_strategies: Dict[str, Any]
    savings_summary: Dict[str, Any]


# Constants
STRICT_NO_CHATTER_NOTE = (
    "Return ONLY the structured fields. "
    "Do not include explanations, reasoning, prefaces, or code fences."
)
