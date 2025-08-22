"""
Consolidation Analysis Page
"""
import streamlit as st
from typing import Dict, List
from src.config.settings import SAMPLE_CONSOLIDATION_OFFERS
from src.utils.api_client import get_eligible_offers, perform_debt_analysis
from src.utils.ui_helpers import (
    show_loading_spinner, show_success_message, show_warning_message,
    show_info_message, display_consolidation_offer, 
    create_two_column_layout, create_three_column_layout, format_currency
)


def display_sample_offers(offers: List[Dict]):
    """Display sample consolidation offers"""
    st.write("**Available Consolidation Offers:**")
    
    for offer in offers:
        with st.expander(f"Offer {offer['offer_id']} - {offer['new_rate_pct']}% APR"):
            col1, col2 = create_two_column_layout()
            
            with col1:
                st.write(f"**Rate:** {offer['new_rate_pct']}%")
                st.write(f"**Max Term:** {offer['max_term_months']} months")
            
            with col2:
                st.write(f"**Max Balance:** {format_currency(offer['max_consolidated_balance'])}")
                st.write(f"**Products:** {', '.join(offer['product_types_eligible'])}")
            
            st.write(f"**Conditions:** {offer['conditions']}")


def display_eligible_offers(eligible_offers: List[Dict]):
    """Display eligible consolidation offers"""
    st.subheader("✅ Eligible Offers")
    
    for offer in eligible_offers:
        display_consolidation_offer(offer)


def display_consolidation_simulation(analysis_result: Dict):
    """Display consolidation simulation results"""
    consolidation = analysis_result.get("consolidation_option")
    if not consolidation:
        return
    
    col1, col2, col3 = create_three_column_layout()
    
    with col1:
        st.metric("Payoff Time", f"{consolidation['months']} months")
    
    with col2:
        st.metric("Total Interest", format_currency(consolidation['total_interest']))
    
    with col3:
        st.metric("Consolidated Amount", format_currency(consolidation['consolidated_amount']))
    
    # Savings analysis
    cons_savings = analysis_result.get("consolidation_savings")
    if cons_savings:
        st.subheader("💰 Savings Analysis")
        
        vs_min = cons_savings.get("vs_minimum", {})
        vs_opt = cons_savings.get("vs_optimized", {})
        
        col1, col2 = create_two_column_layout()
        
        with col1:
            st.success(f"**vs Minimum Payments:**\n\n{format_currency(vs_min.get('interest_saved', 0))} interest saved\n\n{vs_min.get('months_saved', 0)} months faster")
        
        with col2:
            if vs_opt.get('interest_saved', 0) >= 0:
                st.success(f"**vs Optimized Payments:**\n\n{format_currency(vs_opt.get('interest_saved', 0))} interest saved\n\n{abs(vs_opt.get('months_saved', 0))} months difference")
            else:
                st.warning(f"**vs Optimized Payments:**\n\n{format_currency(abs(vs_opt.get('interest_saved', 0)))} more interest\n\n{abs(vs_opt.get('months_saved', 0))} months longer")


def show_consolidation_analysis(customer_id: str, profile: Dict, summary: Dict):
    """Consolidation Analysis Page"""
    
    st.header(f"🏦 Consolidation Analysis - {customer_id}")
    
    # Offer Configuration
    st.subheader("Configure Consolidation Offers")
    
    # Display sample offers
    display_sample_offers(SAMPLE_CONSOLIDATION_OFFERS)
    
    # Credit Score Input
    current_score = summary.get("current_credit_score", 720)
    credit_score = st.number_input(
        "Current Credit Score",
        min_value=300,
        max_value=850,
        value=current_score,
        help="Enter the most recent credit score for eligibility assessment"
    )
    
    # Eligibility Check
    if st.button("Check Offer Eligibility", type="primary"):
        with show_loading_spinner("Evaluating offer eligibility..."):
            eligibility_result = get_eligible_offers(customer_id, SAMPLE_CONSOLIDATION_OFFERS, credit_score)
        
        if eligibility_result:
            show_success_message("Eligibility check completed!")
            
            eligible_offers = eligibility_result.get("eligible_offers", [])
            total_evaluated = eligibility_result.get("total_offers_evaluated", 0)
            
            show_info_message(f"Evaluated {total_evaluated} offers, {len(eligible_offers)} are eligible")
            
            if eligible_offers:
                display_eligible_offers(eligible_offers)
                
                # Consolidation Simulation
                st.subheader("🧮 Consolidation Simulation")
                
                selected_offer_id = st.selectbox(
                    "Select offer to simulate",
                    [offer["offer_id"] for offer in eligible_offers]
                )
                
                if st.button("Simulate Consolidation"):
                    selected_offer = next(offer for offer in eligible_offers if offer["offer_id"] == selected_offer_id)
                    
                    with show_loading_spinner("Simulating consolidation..."):
                        analysis_result = perform_debt_analysis(customer_id, [selected_offer])
                    
                    if analysis_result and analysis_result.get("consolidation_option"):
                        display_consolidation_simulation(analysis_result)
            
            else:
                show_warning_message("No eligible offers found for your current credit profile")
                show_info_message("Consider improving your credit score to access better consolidation options")
        
        else:
            show_warning_message("Failed to check eligibility. Please try again.")
