"""
Data Management Page
"""
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, List, Any
from src.utils.charts import (
    create_loan_portfolio_chart, create_card_balance_chart,
    create_payment_history_chart, create_credit_score_trend
)
from src.utils.ui_helpers import create_three_column_layout, format_currency, safe_numeric_parse, safe_int_parse


def normalize_loan_data(loans: List[Dict]) -> List[Dict]:
    """Normalize loan data ensuring numeric fields are properly parsed"""
    normalized_loans = []
    
    for loan in loans:
        normalized_loan = loan.copy()
        
        # Parse numeric fields
        normalized_loan['principal'] = safe_numeric_parse(loan.get('principal', 0))
        normalized_loan['balance'] = safe_numeric_parse(loan.get('balance', 0))
        normalized_loan['annual_rate_pct'] = safe_numeric_parse(loan.get('annual_rate_pct', 0))
        normalized_loan['monthly_payment'] = safe_numeric_parse(loan.get('monthly_payment', 0))
        normalized_loan['days_past_due'] = safe_int_parse(loan.get('days_past_due', 0))
        normalized_loan['term_months'] = safe_int_parse(loan.get('term_months', 0))
        
        normalized_loans.append(normalized_loan)
    
    return normalized_loans


def normalize_card_data(cards: List[Dict]) -> List[Dict]:
    """Normalize card data ensuring numeric fields are properly parsed"""
    normalized_cards = []
    
    for card in cards:
        normalized_card = card.copy()
        
        # Parse numeric fields
        normalized_card['balance'] = safe_numeric_parse(card.get('balance', 0))
        normalized_card['credit_limit'] = safe_numeric_parse(card.get('credit_limit', 0))
        normalized_card['annual_rate_pct'] = safe_numeric_parse(card.get('annual_rate_pct', 0))
        normalized_card['minimum_payment'] = safe_numeric_parse(card.get('minimum_payment', 0))
        normalized_card['days_past_due'] = safe_int_parse(card.get('days_past_due', 0))
        
        # Calculate utilization if not present
        if 'utilization_pct' not in normalized_card or normalized_card.get('utilization_pct') is None:
            credit_limit = normalized_card['credit_limit']
            balance = normalized_card['balance']
            if credit_limit > 0:
                normalized_card['utilization_pct'] = round((balance / credit_limit) * 100, 2)
            else:
                normalized_card['utilization_pct'] = 0.0
        else:
            normalized_card['utilization_pct'] = safe_numeric_parse(card.get('utilization_pct', 0))
        
        normalized_cards.append(normalized_card)
    
    return normalized_cards


def normalize_payment_data(payments: List[Dict]) -> List[Dict]:
    """Normalize payment data ensuring numeric fields are properly parsed"""
    normalized_payments = []
    
    for payment in payments:
        normalized_payment = payment.copy()
        
        # Parse numeric fields
        normalized_payment['amount'] = safe_numeric_parse(payment.get('amount', 0))
        
        # Ensure date is in proper format
        if 'date' not in normalized_payment:
            normalized_payment['date'] = '2024-01-01'  # Default date
        
        normalized_payments.append(normalized_payment)
    
    return normalized_payments


def normalize_credit_score_data(credit_scores: List[Dict]) -> List[Dict]:
    """Normalize credit score data ensuring numeric fields are properly parsed"""
    normalized_scores = []
    
    for score in credit_scores:
        normalized_score = score.copy()
        
        # Parse numeric fields
        normalized_score['credit_score'] = safe_int_parse(score.get('credit_score', 600))
        
        # Ensure score is within valid range
        if normalized_score['credit_score'] < 300:
            normalized_score['credit_score'] = 300
        elif normalized_score['credit_score'] > 850:
            normalized_score['credit_score'] = 850
        
        # Ensure date is in proper format
        if 'date' not in normalized_score:
            normalized_score['date'] = '2024-01-01'  # Default date
        
        normalized_scores.append(normalized_score)
    
    return normalized_scores


def render_loan_portfolio_tab(loans):
    """Render loan portfolio tab"""
    st.subheader("💼 Loan Portfolio")
    
    if loans:
        # Normalize loan data
        normalized_loans = normalize_loan_data(loans)
        loan_df = pd.DataFrame(normalized_loans)
        
        # Summary metrics
        col1, col2, col3 = create_three_column_layout()
        
        with col1:
            total_loan_balance = loan_df["principal"].sum()
            st.metric("Total Loan Balance", format_currency(total_loan_balance))
        
        with col2:
            avg_rate = loan_df["annual_rate_pct"].mean()
            st.metric("Average Rate", f"{avg_rate:.2f}%")
        
        with col3:
            overdue_loans = len(loan_df[loan_df["days_past_due"] > 0])
            st.metric("Overdue Loans", overdue_loans)
        
        # Format numeric columns for display
        display_df = loan_df.copy()
        if 'principal' in display_df.columns:
            display_df['principal'] = display_df['principal'].apply(lambda x: f"${x:,.2f}")
        if 'balance' in display_df.columns:
            display_df['balance'] = display_df['balance'].apply(lambda x: f"${x:,.2f}")
        if 'monthly_payment' in display_df.columns:
            display_df['monthly_payment'] = display_df['monthly_payment'].apply(lambda x: f"${x:,.2f}")
        if 'annual_rate_pct' in display_df.columns:
            display_df['annual_rate_pct'] = display_df['annual_rate_pct'].apply(lambda x: f"{x:.2f}%")
        
        # Detailed table
        st.dataframe(display_df, use_container_width=True)
        
        # Visualization
        create_loan_portfolio_chart(normalized_loans)
    
    else:
        st.info("No loans found for this customer")


def render_credit_cards_tab(cards):
    """Render credit cards tab"""
    st.subheader("💳 Credit Card Portfolio")
    
    if cards:
        # Normalize card data
        normalized_cards = normalize_card_data(cards)
        card_df = pd.DataFrame(normalized_cards)
        
        # Summary metrics
        col1, col2, col3 = create_three_column_layout()
        
        with col1:
            total_card_balance = card_df["balance"].sum()
            st.metric("Total Card Balance", format_currency(total_card_balance))
        
        with col2:
            avg_rate = card_df["annual_rate_pct"].mean()
            st.metric("Average Rate", f"{avg_rate:.2f}%")
        
        with col3:
            overdue_cards = len(card_df[card_df["days_past_due"] > 0])
            st.metric("Overdue Cards", overdue_cards)
        
        # Format numeric columns for display
        display_df = card_df.copy()
        if 'balance' in display_df.columns:
            display_df['balance'] = display_df['balance'].apply(lambda x: f"${x:,.2f}")
        if 'credit_limit' in display_df.columns:
            display_df['credit_limit'] = display_df['credit_limit'].apply(lambda x: f"${x:,.2f}")
        if 'minimum_payment' in display_df.columns:
            display_df['minimum_payment'] = display_df['minimum_payment'].apply(lambda x: f"${x:,.2f}")
        if 'annual_rate_pct' in display_df.columns:
            display_df['annual_rate_pct'] = display_df['annual_rate_pct'].apply(lambda x: f"{x:.2f}%")
        if 'utilization_pct' in display_df.columns:
            display_df['utilization_pct'] = display_df['utilization_pct'].apply(lambda x: f"{x:.1f}%")
        
        # Detailed table
        st.dataframe(display_df, use_container_width=True)
        
        # Visualization
        create_card_balance_chart(normalized_cards)
    
    else:
        st.info("No credit cards found for this customer")


def render_payments_tab(payments):
    """Render payments tab"""
    st.subheader("💰 Payment History")
    
    if payments:
        # Normalize payment data
        normalized_payments = normalize_payment_data(payments)
        payment_df = pd.DataFrame(normalized_payments)
        
        # Convert date column
        try:
            payment_df["date"] = pd.to_datetime(payment_df["date"])
        except Exception as e:
            st.warning(f"Date parsing issue: {e}")
            # Create a default date column if parsing fails
            payment_df["date"] = pd.to_datetime('2024-01-01')
        
        # Summary metrics
        col1, col2, col3 = create_three_column_layout()
        
        with col1:
            total_payments = payment_df["amount"].sum()
            st.metric("Total Payments", format_currency(total_payments))
        
        with col2:
            avg_payment = payment_df["amount"].mean()
            st.metric("Average Payment", format_currency(avg_payment))
        
        with col3:
            payment_count = len(payment_df)
            st.metric("Payment Count", payment_count)
        
        # Format for display
        display_df = payment_df.copy()
        if 'amount' in display_df.columns:
            display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:,.2f}")
        if 'date' in display_df.columns:
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        
        # Detailed table
        st.dataframe(display_df, use_container_width=True)
        
        # Payment timeline
        create_payment_history_chart(normalized_payments)
    
    else:
        st.info("No payment history found for this customer")


def render_credit_scores_tab(credit_scores):
    """Render credit scores tab"""
    st.subheader("📈 Credit Score History")
    
    if credit_scores:
        # Normalize credit score data
        normalized_scores = normalize_credit_score_data(credit_scores)
        score_df = pd.DataFrame(normalized_scores)
        
        # Convert date column
        try:
            score_df["date"] = pd.to_datetime(score_df["date"])
        except Exception as e:
            st.warning(f"Date parsing issue: {e}")
            # Create a default date column if parsing fails
            score_df["date"] = pd.to_datetime('2024-01-01')
        
        # Summary metrics
        col1, col2, col3 = create_three_column_layout()
        
        with col1:
            current_score = score_df.loc[score_df["date"].idxmax(), "credit_score"]
            st.metric("Current Score", current_score)
        
        with col2:
            avg_score = score_df["credit_score"].mean()
            st.metric("Average Score", f"{avg_score:.0f}")
        
        with col3:
            score_change = score_df["credit_score"].diff().iloc[-1] if len(score_df) > 1 else 0
            st.metric("Recent Change", f"{score_change:+.0f}")
        
        # Format for display
        display_df = score_df.copy()
        if 'date' in display_df.columns:
            display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        
        # Detailed table
        st.dataframe(display_df, use_container_width=True)
        
        # Score trend
        create_credit_score_trend(normalized_scores)
    
    else:
        st.info("No credit score history found for this customer")


def show_data_management(customer_id: str, profile: Dict, summary: Dict):
    """Data Management Page"""
    
    st.header(f"📊 Data Management - {customer_id}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Loans", "Credit Cards", "Payments", "Credit Scores"])
    
    # Loans Tab
    with tab1:
        loans = profile.get("loans", [])
        render_loan_portfolio_tab(loans)
    
    # Credit Cards Tab
    with tab2:
        cards = profile.get("cards", [])
        render_credit_cards_tab(cards)
    
    # Payments Tab
    with tab3:
        payments = profile.get("payments_history", [])
        render_payments_tab(payments)
    
    # Credit Scores Tab  
    with tab4:
        credit_scores = profile.get("credit_scores", [])
        render_credit_scores_tab(credit_scores)
