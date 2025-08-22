"""
Refactored PDF Report Service using LangGraph workflow.
This service coordinates the generation of comprehensive PDF financial reports.
"""

import logging
from typing import Optional
from datetime import datetime
from langgraph.graph import StateGraph, END

from ..schemas.analysis import DebtAnalysisResult
from ..schemas.pdf_report import ReportState, MarkdownDoc
from ..core.llm_utils import (
    get_llm, 
    generate_analysis_prompt, 
    generate_markdown_formatting_prompt,
    generate_html_conversion_prompt,
    invoke_llm_for_analysis,
    invoke_llm_for_markdown,
    invoke_llm_for_html
)
from ..core.html_utils import (
    strip_code_fences,
    remove_html_wrappers,
    ensure_table_sections,
    extract_html_body_fragment,
    markdown_to_html_fallback,
    validate_html_fragment
)
from ..core.report_styles import create_styled_html_document
from ..core.report_utils import (
    prepare_analysis_context,
    generate_fallback_analysis,
    generate_fallback_markdown,
    assemble_markdown_from_structured_response
)
from ..core.pdf_utils import html_to_pdf, simple_html_to_pdf, save_pdf_to_file


class PDFReportService:
    """Service for generating comprehensive PDF reports using LangGraph."""

    def __init__(self, llm=None):
        self.llm = llm or get_llm()
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow for PDF report generation."""
        workflow = StateGraph(ReportState)
        
        # Add nodes
        workflow.add_node("generate_text", self._generate_analysis_text)
        workflow.add_node("format_markdown", self._format_to_markdown)
        workflow.add_node("convert_to_pdf", self._convert_to_styled_html_and_pdf)
        
        # Add edges
        workflow.set_entry_point("generate_text")
        workflow.add_edge("generate_text", "format_markdown")
        workflow.add_edge("format_markdown", "convert_to_pdf")
        workflow.add_edge("convert_to_pdf", END)
        
        return workflow.compile()

    def _generate_analysis_text(self, state: ReportState) -> ReportState:
        """Node 1: Generate comprehensive text analysis from the debt analysis data."""
        analysis = state["analysis_data"]
        
        # Prepare the analysis context
        context = prepare_analysis_context(analysis)
        
        # Generate the prompt and invoke LLM
        prompt = generate_analysis_prompt(analysis, context)
        
        try:
            raw_analysis = invoke_llm_for_analysis(self.llm, prompt)
        except Exception as e:
            logging.error(f"LLM analysis generation failed: {e}")
            raw_analysis = generate_fallback_analysis(analysis)

        state["raw_analysis"] = raw_analysis
        return state

    def _format_to_markdown(self, state: ReportState) -> ReportState:
        """Node 2: Format the analysis text into structured markdown for PDF conversion."""
        raw_analysis = state["raw_analysis"]
        analysis = state["analysis_data"]

        prompt = generate_markdown_formatting_prompt(raw_analysis, analysis)

        try:
            resp: MarkdownDoc = invoke_llm_for_markdown(self.llm, prompt)

            # Prefer the model's full 'markdown' if present; otherwise assemble from sections.
            if resp.markdown and resp.markdown.strip():
                markdown_content = resp.markdown.strip()
            else:
                markdown_content = assemble_markdown_from_structured_response(resp)

        except Exception as e:
            logging.error(f"Markdown formatting failed: {e}")
            markdown_content = generate_fallback_markdown(analysis, raw_analysis)

        state["markdown_content"] = markdown_content
        return state

    def _convert_to_styled_html_and_pdf(self, state: ReportState) -> ReportState:
        """Node 3: Convert markdown to styled HTML and then to PDF."""
        markdown_content = state["markdown_content"]
        
        # Convert markdown to HTML
        html_content = self._markdown_to_html_with_llm(markdown_content)

        # Extract the body content from the HTML
        body_content = extract_html_body_fragment(html_content)

        # Add professional styling
        styled_html = create_styled_html_document(body_content)
        state["styled_html"] = styled_html
        
        # Convert HTML to PDF
        try:
            pdf_bytes = html_to_pdf(styled_html)
            state["pdf_bytes"] = pdf_bytes
        except Exception as e:
            logging.error(f"Error converting HTML to PDF: {e}")
            # Fallback to simple HTML to PDF conversion
            state["pdf_bytes"] = simple_html_to_pdf(html_content)
        
        return state

    def _markdown_to_html_with_llm(self, markdown_content: str) -> str:
        """Use LLM (structured output) to convert Markdown to a clean HTML fragment."""
        prompt = generate_html_conversion_prompt(markdown_content)
        
        try:
            resp = invoke_llm_for_html(self.llm, prompt)

            # Clean any possible code fences or wrappers the model might still sneak in
            html = strip_code_fences(resp.html)
            html = remove_html_wrappers(html)
            html = ensure_table_sections(html)

            # Minimal sanity: ensure we return *some* HTML; else fallback.
            if not validate_html_fragment(html):
                raise ValueError("Model returned no HTML tags.")

            return html

        except Exception as e:
            logging.error(f"LLM HTML conversion failed: {e}")
            # Fallback to local Markdown conversion
            return markdown_to_html_fallback(markdown_content)

    def generate_financial_report(self, analysis: DebtAnalysisResult) -> bytes:
        """
        Generate a comprehensive PDF financial report using LangGraph workflow.
        
        Args:
            analysis: The debt analysis result data
            
        Returns:
            PDF content as bytes
        """
        initial_state = ReportState(
            analysis_data=analysis,
            raw_analysis="",
            markdown_content="",
            styled_html="",
            pdf_bytes=b""
        )
        
        # Run the LangGraph workflow
        final_state = self.graph.invoke(initial_state)
        
        return final_state["pdf_bytes"]

    def generate_simple_report(self, analysis: DebtAnalysisResult, filename: Optional[str] = None) -> str:
        """
        Generate and save a simple PDF report to /tmp and return its path.
        
        Args:
            analysis: The debt analysis result data
            filename: Optional custom filename
            
        Returns:
            File path where the PDF was saved
        """
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{analysis.customer_id}_{timestamp}.pdf"
        
        pdf_bytes = self.generate_financial_report(analysis)
        filepath = f"/tmp/{filename}"
        
        save_pdf_to_file(pdf_bytes, filepath)
        
        return filepath
