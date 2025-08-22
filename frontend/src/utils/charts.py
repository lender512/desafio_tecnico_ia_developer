"""
Chart and visualization utilities
"""
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
from typing import Dict, List, Any
from src.utils.ui_helpers import safe_numeric_parse


def create_payment_comparison_chart(analysis_result: Dict):
    """Create payment strategy comparison chart"""
    
    st.subheader("📊 Payment Strategy Comparison")
    
    # Extract data with safe parsing
    min_strategy = analysis_result.get("minimum_payment_strategy", {})
    opt_strategy = analysis_result.get("optimized_payment_strategy", {})
    consolidation = analysis_result.get("consolidation_option")
    
    strategies = ["Minimum Payments", "Optimized Payments"]
    months = [
        safe_numeric_parse(min_strategy.get("months", 0)),
        safe_numeric_parse(opt_strategy.get("months", 0))
    ]
    interests = [
        safe_numeric_parse(min_strategy.get("total_interest", 0)),
        safe_numeric_parse(opt_strategy.get("total_interest", 0))
    ]
    
    if consolidation:
        strategies.append("Consolidation")
        months.append(safe_numeric_parse(consolidation.get("months", 0)))
        interests.append(safe_numeric_parse(consolidation.get("total_interest", 0)))
    
    # Create comparison chart
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Payoff Timeline", "Total Interest"],
        specs=[[{"type": "bar"}, {"type": "bar"}]]
    )
    
    # Payoff timeline
    fig.add_trace(
        go.Bar(x=strategies, y=months, name="Months", marker_color=["red", "blue", "green"][:len(strategies)]),
        row=1, col=1
    )
    
    # Total interest
    fig.add_trace(
        go.Bar(x=strategies, y=interests, name="Interest", marker_color=["red", "blue", "green"][:len(strategies)]),
        row=1, col=2
    )
    
    fig.update_layout(
        title="Payment Strategy Comparison",
        showlegend=False,
        height=400
    )
    
    fig.update_yaxes(title_text="Months", row=1, col=1)
    fig.update_yaxes(title_text="Total Interest ($)", row=1, col=2)
    
    st.plotly_chart(fig, use_container_width=True)


def create_simple_payment_timeline(summary: Dict):
    """Create a simple payment timeline projection"""
    
    total_debt = safe_numeric_parse(summary.get("total_debt", 0))
    monthly_payment = safe_numeric_parse(summary.get("total_monthly_payments", 0))
    
    if total_debt > 0 and monthly_payment > 0:
        # Simple projection (assuming no interest for demonstration)
        months = int(total_debt / monthly_payment)
        
        # Create timeline
        timeline_months = list(range(1, min(months + 1, 61)))  # Cap at 60 months for display
        remaining_balance = [max(0, total_debt - (month * monthly_payment)) for month in timeline_months]
        
        df = pd.DataFrame({
            "Month": timeline_months,
            "Remaining Balance": remaining_balance
        })
        
        fig = px.line(
            df,
            x="Month",
            y="Remaining Balance",
            title="Simple Debt Payoff Projection",
            labels={"Remaining Balance": "Remaining Balance ($)"}
        )
        
        fig.update_layout(
            xaxis_title="Month",
            yaxis_title="Remaining Balance ($)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        st.info(f"💡 Based on current monthly payments of ${monthly_payment:,.2f}, debt would be paid off in approximately {months} months (simplified calculation)")
    
    else:
        st.warning("⚠️ Insufficient data for timeline projection")


def create_loan_portfolio_chart(loans: List[Dict]):
    """Create loan portfolio visualization"""
    if not loans:
        return
    
    # Normalize loan data for charting
    normalized_loans = []
    for loan in loans:
        normalized_loan = {
            'loan_id': loan.get('loan_id', 'Unknown'),
            'principal': safe_numeric_parse(loan.get('principal', 0))
        }
        normalized_loans.append(normalized_loan)
    
    loan_df = pd.DataFrame(normalized_loans)
    
    # Filter out zero-value loans
    loan_df = loan_df[loan_df['principal'] > 0]
    
    if len(loan_df) > 1:
        fig = px.pie(
            loan_df, 
            values="principal", 
            names="loan_id",
            title="Loan Portfolio Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    elif len(loan_df) == 1:
        st.info(f"Single loan: {loan_df.iloc[0]['loan_id']} - ${loan_df.iloc[0]['principal']:,.2f}")


def create_card_balance_chart(cards: List[Dict]):
    """Create credit card balance visualization"""
    if not cards:
        return
    
    # Normalize card data for charting
    normalized_cards = []
    for card in cards:
        normalized_card = {
            'card_id': card.get('card_id', 'Unknown'),
            'balance': safe_numeric_parse(card.get('balance', 0)),
            'annual_rate_pct': safe_numeric_parse(card.get('annual_rate_pct', 0))
        }
        normalized_cards.append(normalized_card)
    
    card_df = pd.DataFrame(normalized_cards)
    
    # Filter out zero-balance cards
    card_df = card_df[card_df['balance'] > 0]
    
    if len(card_df) > 1:
        fig = px.bar(
            card_df,
            x="card_id",
            y="balance", 
            color="annual_rate_pct",
            title="Credit Card Balances by Rate",
            labels={"balance": "Balance ($)", "annual_rate_pct": "Annual Rate (%)"}
        )
        st.plotly_chart(fig, use_container_width=True)
    elif len(card_df) == 1:
        st.info(f"Single card: {card_df.iloc[0]['card_id']} - ${card_df.iloc[0]['balance']:,.2f} at {card_df.iloc[0]['annual_rate_pct']:.2f}%")


def create_payment_history_chart(payments: List[Dict]):
    """Create payment history timeline"""
    if not payments:
        return
    
    # Normalize payment data for charting
    normalized_payments = []
    for payment in payments:
        normalized_payment = {
            'date': payment.get('date', '2024-01-01'),
            'amount': safe_numeric_parse(payment.get('amount', 0)),
            'product_type': payment.get('product_type', 'Unknown')
        }
        normalized_payments.append(normalized_payment)
    
    payment_df = pd.DataFrame(normalized_payments)
    
    # Parse dates safely
    try:
        payment_df["date"] = pd.to_datetime(payment_df["date"])
    except Exception:
        # If date parsing fails, create a sequence of dates
        payment_df["date"] = pd.date_range(start='2024-01-01', periods=len(payment_df), freq='M')
    
    # Filter out zero-amount payments
    payment_df = payment_df[payment_df['amount'] > 0]
    
    if len(payment_df) > 1:
        fig = px.line(
            payment_df.sort_values("date"),
            x="date",
            y="amount",
            color="product_type",
            title="Payment History Timeline",
            labels={"amount": "Payment Amount ($)", "date": "Date"}
        )
        st.plotly_chart(fig, use_container_width=True)
    elif len(payment_df) == 1:
        st.info(f"Single payment: ${payment_df.iloc[0]['amount']:,.2f} on {payment_df.iloc[0]['date'].strftime('%Y-%m-%d')}")


def create_credit_score_trend(credit_scores: List[Dict]):
    """Create credit score trend chart"""
    if not credit_scores:
        return
    
    # Normalize credit score data for charting
    normalized_scores = []
    for score in credit_scores:
        normalized_score = {
            'date': score.get('date', '2024-01-01'),
            'credit_score': max(300, min(850, safe_numeric_parse(score.get('credit_score', 600))))  # Clamp to valid range
        }
        normalized_scores.append(normalized_score)
    
    score_df = pd.DataFrame(normalized_scores)
    
    # Parse dates safely
    try:
        score_df["date"] = pd.to_datetime(score_df["date"])
    except Exception:
        # If date parsing fails, create a sequence of dates
        score_df["date"] = pd.date_range(start='2024-01-01', periods=len(score_df), freq='M')
    
    if len(score_df) > 1:
        fig = px.line(
            score_df.sort_values("date"),
            x="date",
            y="credit_score",
            title="Credit Score Trend",
            range_y=[300, 850],
            labels={"credit_score": "Credit Score", "date": "Date"}
        )
        fig.add_hline(y=650, line_dash="dash", line_color="orange", annotation_text="Fair Credit")
        fig.add_hline(y=700, line_dash="dash", line_color="green", annotation_text="Good Credit")
        fig.add_hline(y=750, line_dash="dash", line_color="blue", annotation_text="Excellent Credit")
        st.plotly_chart(fig, use_container_width=True)
    elif len(score_df) == 1:
        score = score_df.iloc[0]['credit_score']
        date = score_df.iloc[0]['date'].strftime('%Y-%m-%d')
        st.info(f"Single score record: {score} on {date}")
