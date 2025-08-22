"""
Customer Dashboard Page
"""
import streamlit as st
from typing import Dict, Any
from src.components.ui_components import (
    render_financial_metrics, render_risk_assessment, 
    render_portfolio_overview, render_cashflow_analysis,
    render_debt_to_income_ratio
)
from src.utils.charts import create_loan_portfolio_chart, create_card_balance_chart
from src.utils.ui_helpers import safe_numeric_parse


def show_customer_dashboard(customer_id: str, profile: Dict, summary: Dict):
    """Customer Dashboard Page"""
    
    st.header(f"Customer Dashboard - {customer_id}")
    
    # Financial Health Overview
    render_financial_metrics(summary)
    
    # Risk Level
    render_risk_assessment(summary)
    
    # Portfolio Overview
    render_portfolio_overview(profile)
    
    # Portfolio Visualizations
    loans = profile.get("loans", [])
    cards = profile.get("cards", [])
    
    if loans:
        create_loan_portfolio_chart(loans)
    
    if cards:
        create_card_balance_chart(cards)
    
    # Cashflow Information
    cashflow = profile.get("cashflow")
    if cashflow:
        render_cashflow_analysis(cashflow)
        
        # Debt-to-Income Ratio
        monthly_payments = safe_numeric_parse(summary.get("total_monthly_payments", 0))
        render_debt_to_income_ratio(cashflow, monthly_payments)
