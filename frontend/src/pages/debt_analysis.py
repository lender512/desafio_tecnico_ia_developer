"""
Debt Analysis Page
"""
import streamlit as st
from typing import Dict, List
from src.utils.api_client import perform_debt_analysis
from src.components.ui_components import (
    render_analysis_results, render_consolidation_results,
    render_consolidation_savings
)
from src.utils.charts import create_payment_comparison_chart
from src.utils.ui_helpers import show_loading_spinner, show_success_message, show_error_message


def create_consolidation_offer_form(num_offers: int) -> List[Dict]:
    """Create consolidation offer configuration form"""
    offers = []
    
    for i in range(num_offers):
        st.write(f"**Offer {i+1}**")
        col1, col2 = st.columns(2)
        
        with col1:
            offer_id = st.text_input(f"Offer ID", value=f"OFFER{i+1:03d}", key=f"offer_id_{i}")
            new_rate = st.number_input(f"New Rate (%)", min_value=0.0, max_value=50.0, value=8.5, key=f"rate_{i}")
            max_term = st.number_input(f"Max Term (months)", min_value=1, max_value=600, value=60, key=f"term_{i}")
        
        with col2:
            max_balance = st.number_input(f"Max Balance", min_value=0.0, value=25000.0, key=f"balance_{i}")
            conditions = st.text_input(f"Conditions", value="Good credit required", key=f"conditions_{i}")
            product_types = st.multiselect(
                f"Eligible Products", 
                ["personal", "credit_card", "auto", "mortgage"],
                default=["personal", "credit_card"],
                key=f"products_{i}"
            )
        
        offers.append({
            "offer_id": offer_id,
            "product_types_eligible": product_types,
            "new_rate_pct": new_rate,
            "max_term_months": int(max_term),
            "max_consolidated_balance": float(max_balance),
            "conditions": conditions
        })
    
    return offers


def show_debt_analysis(customer_id: str, profile: Dict, summary: Dict):
    """Debt Analysis Page"""
    
    st.header(f"🔍 Debt Analysis - {customer_id}")
    
    # Configuration
    st.subheader("Analysis Configuration")
    
    with st.expander("Consolidation Offers"):
        st.write("Add consolidation offers for analysis:")
        
        num_offers = st.number_input("Number of offers", min_value=0, max_value=5, value=1)
        offers = create_consolidation_offer_form(num_offers) if num_offers > 0 else []
    
    # Run Analysis
    if st.button("🔍 Run Comprehensive Analysis", type="primary"):
        with show_loading_spinner("Analyzing debt structure and options..."):
            analysis_result = perform_debt_analysis(customer_id, offers if num_offers > 0 else None)
        
        if analysis_result:
            show_success_message("Analysis completed successfully!")
            
            # Results Display
            render_analysis_results(analysis_result)
            render_consolidation_results(analysis_result)
            render_consolidation_savings(analysis_result)
            
            # Consolidation Message
            message = analysis_result.get("consolidation_message")
            if message:
                st.info(f"💡 **Recommendation:** {message}")
            
            # Visualization
            create_payment_comparison_chart(analysis_result)
        
        else:
            show_error_message("Failed to perform analysis. Please check the API connection.")
