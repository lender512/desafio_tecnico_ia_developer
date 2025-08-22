"""PDF generation utilities using WeasyPrint."""

import logging
from weasyprint import HTML
from typing import Optional

from .report_styles import create_simple_html_document


def html_to_pdf(html_content: str) -> bytes:
    """Convert styled HTML to PDF using WeasyPrint."""
    try:
        html_doc = HTML(string=html_content)
        return html_doc.write_pdf()
    except Exception as e:
        logging.error(f"Error converting HTML to PDF: {e}")
        raise


def simple_html_to_pdf(html_content: str, title: str = "Financial Report") -> bytes:
    """
    Fallback method for HTML to PDF conversion with simple styling.
    
    Args:
        html_content: The HTML content to convert
        title: Document title
        
    Returns:
        PDF bytes
    """
    try:
        simple_html = create_simple_html_document(html_content, title)
        html_doc = HTML(string=simple_html)
        return html_doc.write_pdf()
    except Exception as e:
        logging.error(f"Fallback PDF generation failed: {e}")
        # Return empty bytes if all else fails
        return b""


def save_pdf_to_file(pdf_bytes: bytes, filepath: str) -> None:
    """
    Save PDF bytes to a file.
    
    Args:
        pdf_bytes: The PDF content as bytes
        filepath: Path where to save the file
    """
    try:
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
    except Exception as e:
        logging.error(f"Error saving PDF to file {filepath}: {e}")
        raise
