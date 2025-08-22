"""
Common UI components
"""
import streamlit as st
from typing import Dict, List, Any
from src.utils.ui_helpers import (
    format_currency, format_percentage, get_risk_indicator,
    create_four_column_layout, create_three_column_layout, create_two_column_layout,
    safe_numeric_parse
)


def render_financial_metrics(summary: Dict):
    """Render financial health overview metrics"""
    st.subheader("📊 Financial Health Overview")
    
    col1, col2, col3, col4 = create_four_column_layout()
    
    with col1:
        debt_amount = safe_numeric_parse(summary.get("total_debt", 0))
        st.metric(
            label="Total Debt",
            value=format_currency(debt_amount)
        )
    
    with col2:
        monthly_payments = safe_numeric_parse(summary.get("total_monthly_payments", 0))
        st.metric(
            label="Monthly Payments",
            value=format_currency(monthly_payments)
        )
    
    with col3:
        credit_score = safe_numeric_parse(summary.get("current_credit_score", 0))
        st.metric(
            label="Credit Score",
            value=f"{credit_score:.0f}"
        )
    
    with col4:
        health_score = safe_numeric_parse(summary.get("financial_health_score", 0))
        st.metric(
            label="Health Score",
            value=f"{health_score:.0f}/100"
        )


def render_risk_assessment(summary: Dict):
    """Render risk level assessment"""
    risk_level = summary.get("risk_level", "unknown")
    risk_color = get_risk_indicator(risk_level)
    st.markdown(f"**Risk Level:** {risk_color} {risk_level.title()}")


def render_portfolio_overview(profile: Dict):
    """Render portfolio overview with loans and cards"""
    st.subheader("💳 Portfolio Overview")
    
    col1, col2 = create_two_column_layout()
    
    with col1:
        st.write("**Loans**")
        loans = profile.get("loans", [])
        if loans:
            import pandas as pd
            loan_df = pd.DataFrame(loans)
            st.dataframe(loan_df[["loan_id", "product_type", "principal", "annual_rate_pct", "days_past_due"]])
        else:
            st.info("No loans found")
    
    with col2:
        st.write("**Credit Cards**")
        cards = profile.get("cards", [])
        if cards:
            import pandas as pd
            card_df = pd.DataFrame(cards)
            st.dataframe(card_df[["card_id", "balance", "annual_rate_pct", "days_past_due"]])
        else:
            st.info("No credit cards found")


def render_cashflow_analysis(cashflow: Dict):
    """Render cashflow analysis section"""
    if not cashflow:
        return
    
    st.subheader("💰 Cashflow Analysis")
    col1, col2, col3 = create_three_column_layout()
    
    with col1:
        income = safe_numeric_parse(cashflow.get("monthly_income_avg", 0))
        st.metric("Monthly Income", format_currency(income))
    
    with col2:
        expenses = safe_numeric_parse(cashflow.get("essential_expenses_avg", 0))
        st.metric("Essential Expenses", format_currency(expenses))
    
    with col3:
        variability = safe_numeric_parse(cashflow.get("income_variability_pct", 0))
        st.metric("Income Variability", format_percentage(variability))


def render_debt_to_income_ratio(cashflow: Dict, monthly_payments: float):
    """Render debt-to-income ratio"""
    if not cashflow:
        return
    
    income = safe_numeric_parse(cashflow.get("monthly_income_avg", 0))
    monthly_payments = safe_numeric_parse(monthly_payments, 0)
    
    if income > 0:
        dti_ratio = (monthly_payments / income) * 100
        st.metric("Debt-to-Income Ratio", format_percentage(dti_ratio))


def render_analysis_results(analysis_result: Dict):
    """Render debt analysis results"""
    st.subheader("📈 Analysis Results")
    
    # Key Metrics
    col1, col2, col3 = create_three_column_layout()
    
    with col1:
        min_strategy = analysis_result.get("minimum_payment_strategy", {})
        months = safe_numeric_parse(min_strategy.get('months', 0))
        interest = safe_numeric_parse(min_strategy.get('total_interest', 0))
        st.metric(
            "Minimum Payments",
            f"{months:.0f} months",
            delta=f"${interest:,.0f} interest"
        )
    
    with col2:
        opt_strategy = analysis_result.get("optimized_payment_strategy", {})
        months = safe_numeric_parse(opt_strategy.get('months', 0))
        interest = safe_numeric_parse(opt_strategy.get('total_interest', 0))
        st.metric(
            "Optimized Payments", 
            f"{months:.0f} months",
            delta=f"${interest:,.0f} interest"
        )
    
    with col3:
        savings = analysis_result.get("savings_vs_minimum", {})
        months_saved = safe_numeric_parse(savings.get('months_saved', 0))
        interest_saved = safe_numeric_parse(savings.get('interest_saved', 0))
        st.metric(
            "Optimized Savings",
            f"{months_saved:.0f} months",
            delta=f"${interest_saved:,.0f} saved"
        )


def render_consolidation_results(analysis_result: Dict):
    """Render consolidation analysis results"""
    consolidation = analysis_result.get("consolidation_option")
    if not consolidation:
        return
    
    st.subheader("🏦 Consolidation Analysis")
    
    col1, col2, col3, col4 = create_four_column_layout()
    
    with col1:
        st.metric("Offer ID", consolidation.get("offer_id", "N/A"))
    
    with col2:
        st.metric("New Rate", f"{consolidation.get('new_rate_pct', 0)}%")
    
    with col3:
        st.metric("Term", f"{consolidation.get('months', 0)} months")
    
    with col4:
        st.metric("Total Interest", format_currency(consolidation.get('total_interest', 0)))


def render_consolidation_savings(analysis_result: Dict):
    """Render consolidation savings comparison"""
    cons_savings = analysis_result.get("consolidation_savings", {})
    if not cons_savings:
        return
    
    st.write("**Consolidation Savings:**")
    
    vs_min = cons_savings.get("vs_minimum", {})
    vs_opt = cons_savings.get("vs_optimized", {})
    
    col1, col2 = create_two_column_layout()
    
    with col1:
        st.info(f"**vs Minimum:** {format_currency(vs_min.get('interest_saved', 0))} saved, {vs_min.get('months_saved', 0)} months faster")
    
    with col2:
        if vs_opt.get('interest_saved', 0) > 0:
            st.success(f"**vs Optimized:** {format_currency(vs_opt.get('interest_saved', 0))} saved, {abs(vs_opt.get('months_saved', 0))} months difference")
        else:
            st.warning(f"**vs Optimized:** {format_currency(abs(vs_opt.get('interest_saved', 0)))} more interest, {abs(vs_opt.get('months_saved', 0))} months longer")


def render_simulation_results(result: Dict, title: str):
    """Render payment simulation results"""
    if not result:
        st.error("Simulation failed")
        return
    
    st.success("✅ Simulation completed!")
    
    months = result.get("months", 0)
    total_interest = result.get("total_interest", 0)
    
    st.metric("Payoff Time", f"{months} months")
    st.metric("Total Interest", format_currency(total_interest))
