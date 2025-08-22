"""
Payment Simulations Page
"""
import streamlit as st
from typing import Dict
from src.utils.api_client import simulate_payments
from src.components.ui_components import render_simulation_results
from src.utils.charts import create_simple_payment_timeline
from src.utils.ui_helpers import show_loading_spinner, format_currency


def show_payment_simulations(customer_id: str, profile: Dict, summary: Dict):
    """Payment Simulations Page"""
    
    st.header(f"📊 Payment Simulations - {customer_id}")
    
    col1, col2 = st.columns(2)
    
    # Minimum Payment Simulation
    with col1:
        st.subheader("💸 Minimum Payment Strategy")
        
        if st.button("Simulate Minimum Payments", key="min_sim"):
            with show_loading_spinner("Simulating minimum payment strategy..."):
                min_result = simulate_payments(customer_id, "minimum")
            
            render_simulation_results(min_result, "Minimum Payments")
            
            if min_result:
                # Calculate monthly payment estimate
                months = min_result.get("months", 0)
                total_interest = min_result.get("total_interest", 0)
                total_debt = float(summary.get("total_debt", 0))
                
                if months > 0:
                    avg_monthly = (total_debt + total_interest) / months
                    st.metric("Avg Monthly Payment", format_currency(avg_monthly))
    
    # Optimized Payment Simulation  
    with col2:
        st.subheader("🎯 Optimized Payment Strategy")
        
        if st.button("Simulate Optimized Payments", key="opt_sim"):
            with show_loading_spinner("Simulating optimized payment strategy..."):
                opt_result = simulate_payments(customer_id, "optimized")
            
            render_simulation_results(opt_result, "Optimized Payments")
            
            if opt_result:
                # Calculate monthly payment estimate
                months = opt_result.get("months", 0)
                total_interest = opt_result.get("total_interest", 0)
                total_debt = float(summary.get("total_debt", 0))
                
                if months > 0:
                    avg_monthly = (total_debt + total_interest) / months
                    st.metric("Avg Monthly Payment", format_currency(avg_monthly))
    
    # Payment Timeline Visualization
    st.subheader("📈 Payment Timeline Analysis")
    
    if st.button("Generate Payment Timeline", type="primary"):
        st.info("💡 Detailed payment timeline visualization would require additional API endpoints for monthly breakdowns.")
        create_simple_payment_timeline(summary)
