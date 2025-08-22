"""
PDF Reports Page
"""
import streamlit as st
from datetime import datetime
from typing import Dict, List
from src.config.settings import SAMPLE_CONSOLIDATION_OFFERS
from src.utils.api_client import (
    generate_pdf_report, 
    download_pdf_report
)
from src.utils.ui_helpers import (
    show_loading_spinner, show_success_message, show_error_message,
    show_info_message, create_two_column_layout
)


def render_report_configuration():
    """Render report configuration form"""
    st.subheader("Report Configuration")
    
    col1, col2 = create_two_column_layout()
    
    with col1:
        report_title = st.text_input(
            "Report Title",
            value="Financial Analysis Report"
        )
        
        include_consolidation = st.checkbox(
            "Include Consolidation Analysis",
            value=True,
            help="Include consolidation options and recommendations in the report"
        )
    
    with col2:
        pass
    
    return report_title, include_consolidation


def render_consolidation_offers_selection():
    """Render consolidation offers selection for report"""
    st.subheader("Consolidation Offers for Report")
    
    selected_offers = st.multiselect(
        "Select offers to include in report",
        [f"{offer['offer_id']} - {offer['new_rate_pct']}%" for offer in SAMPLE_CONSOLIDATION_OFFERS],
        default=[f"{offer['offer_id']} - {offer['new_rate_pct']}%" for offer in SAMPLE_CONSOLIDATION_OFFERS]
    )
    
    # Filter selected offers
    offers_for_report = []
    for offer_str in selected_offers:
        offer_id = offer_str.split(" - ")[0]
        offer = next(o for o in SAMPLE_CONSOLIDATION_OFFERS if o["offer_id"] == offer_id)
        offers_for_report.append(offer)
    
    return offers_for_report


def render_report_generation_buttons(customer_id: str, offers_for_report: List[Dict], report_title: str):
    """Render report generation buttons"""
    st.subheader("Generate Report")
    
    col1, col2 = create_two_column_layout()
    
    with col1:
        if st.button("📄 Generate PDF Report", type="primary"):
            with show_loading_spinner("Generating comprehensive financial report..."):
                report_result = generate_pdf_report(customer_id, offers_for_report, report_title)

            if report_result:
                if report_result.get("report_generated"):
                    show_success_message("Report generated successfully!")
                    
                    filename = report_result.get("filename", "")
                    file_size = report_result.get("file_size_bytes", 0)
                    
                    col1_metric, col2_metric = create_two_column_layout()
                    
                    with col1_metric:
                        st.metric("Filename", filename)
                    
                    with col2_metric:
                        st.metric("File Size", f"{file_size:,} bytes")
                    
                    # Download button for generated report
                    if filename:
                        try:
                            with show_loading_spinner("Preparing download..."):
                                pdf_content = download_pdf_report(customer_id, filename)
                            
                            if pdf_content:
                                st.download_button(
                                    label="📥 Download Report",
                                    data=pdf_content,
                                    file_name=filename,
                                    mime="application/pdf",
                                    type="primary"
                                )
                                show_info_message(f"Click the button above to download: {filename}")
                            else:
                                show_error_message("Failed to retrieve report file")
                                
                        except Exception as e:
                            show_error_message(f"Download error: {str(e)}")
                
                else:
                    show_error_message("Failed to generate report")
            
            else:
                show_error_message("Report generation failed. Please check the API connection.")
    
    with col2:
        pass


def render_report_contents_preview():
    """Render report contents preview"""
    st.subheader("📋 Report Contents Preview")
    
    st.write("The generated report will include:")
    
    col1, col2 = create_two_column_layout()
    
    with col1:
        st.write("**Customer Information:**")
        st.write("• Customer ID and basic profile")
        st.write("• Current financial position")
        st.write("• Credit score and risk assessment")
        
        st.write("**Debt Portfolio:**")
        st.write("• Loan details and balances")
        st.write("• Credit card information") 
        st.write("• Payment obligations summary")
    
    with col2:
        st.write("**Payment Analysis:**")
        st.write("• Minimum payment strategy")
        st.write("• Optimized payment strategy")
        st.write("• Interest and time savings")
        
        st.write("**Consolidation Analysis:**")
        st.write("• Eligible consolidation offers")
        st.write("• Consolidation simulations")
        st.write("• Savings comparisons")


def render_report_history():
    """Render report history section"""
    st.subheader("📚 Report History")
    show_info_message("Historical report management would require additional database functionality to track generated reports")


def show_pdf_reports(customer_id: str, profile: Dict, summary: Dict):
    """PDF Reports Page"""
    
    st.header(f"📄 PDF Reports - {customer_id}")
    
    # Report Configuration
    report_title, include_consolidation = render_report_configuration()
    
    # Consolidation Offers for Report
    offers_for_report = []
    if include_consolidation:
        offers_for_report = render_consolidation_offers_selection()
    
    # Generate Report
    render_report_generation_buttons(customer_id, offers_for_report, report_title)

    # Report Preview
    render_report_contents_preview()
    
    # Historical Reports
    render_report_history()
