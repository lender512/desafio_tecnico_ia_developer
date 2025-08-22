"""Utilities for preparing report context and fallback content generation."""

import logging
from typing import Dict
from datetime import datetime

from ..schemas.analysis import DebtAnalysisResult


def prepare_analysis_context(analysis: DebtAnalysisResult) -> Dict[str, str]:
    """Prepare context data for analysis generation."""
    context = {
        "consolidation": ""
    }

    if getattr(analysis, "consolidation_option", None):
        context["consolidation"] = (
            f"Consolidation Option Available:\n"
            f"- Offer ID: {analysis.consolidation_option.offer_id}\n"
            f"- New Interest Rate: {analysis.consolidation_option.new_rate_pct}%\n"
            f"- Duration: {analysis.consolidation_option.months} months\n"
            f"- Total Interest: ${analysis.consolidation_option.total_interest:,.2f}\n"
            f"- Consolidated Amount: ${analysis.consolidation_option.consolidated_amount:,.2f}\n\n"
            f"Consolidation vs Minimum Savings: ${analysis.consolidation_savings.vs_minimum.interest_saved:,.2f} interest, {analysis.consolidation_savings.vs_minimum.months_saved} months\n"
            f"Consolidation vs Optimized Savings: ${analysis.consolidation_savings.vs_optimized.interest_saved:,.2f} interest, {analysis.consolidation_savings.vs_optimized.months_saved} months"
        )
    else:
        context["consolidation"] = getattr(
            analysis, "consolidation_message", "No consolidation options are currently available for this customer."
        )

    return context


def generate_fallback_analysis(analysis: DebtAnalysisResult) -> str:
    """Generate fallback analysis if LLM fails."""
    return f"""
    Financial Analysis for Customer {analysis.customer_id}

    Current Credit Score: {analysis.current_credit_score}

    Payment Strategy Comparison:
    - Minimum Payment: {analysis.minimum_payment_strategy.months} months, ${analysis.minimum_payment_strategy.total_interest:,.2f} total interest
    - Optimized Payment: {analysis.optimized_payment_strategy.months} months, ${analysis.optimized_payment_strategy.total_interest:,.2f} total interest
    - Potential Savings: ${analysis.savings_vs_minimum.interest_saved:,.2f} in interest and {analysis.savings_vs_minimum.months_saved} months

    The optimized payment strategy offers significant benefits over the minimum payment approach, allowing the customer to save both time and money.

    Recommendations:
    1. Adopt the optimized payment strategy to maximize savings
    2. Monitor credit score improvements over time
    3. Consider additional debt reduction strategies
    """


def generate_fallback_markdown(analysis: DebtAnalysisResult, raw_analysis: str) -> str:
    """Generate fallback markdown if formatting fails."""
    return f"""
# Personal Financial Analysis Report

**Customer ID:** {analysis.customer_id}  
**Report Date:** {datetime.now().strftime("%B %d, %Y")}  
**Credit Score:** {analysis.current_credit_score}

## Analysis

{raw_analysis}

## Financial Summary

| Strategy | Duration (Months) | Total Interest |
|----------|------------------|----------------|
| Minimum Payment | {analysis.minimum_payment_strategy.months} | ${analysis.minimum_payment_strategy.total_interest:,.2f} |
| Optimized Payment | {analysis.optimized_payment_strategy.months} | ${analysis.optimized_payment_strategy.total_interest:,.2f} |

## Savings Potential

- **Interest Saved:** ${analysis.savings_vs_minimum.interest_saved:,.2f}
- **Time Saved:** {analysis.savings_vs_minimum.months_saved} months

## Recommendations

- Adopt the optimized payment strategy
- Monitor progress regularly
- Consider additional financial optimization opportunities
    """


def assemble_markdown_from_structured_response(resp, fallback_title: str = "Personal Financial Analysis Report") -> str:
    """Assemble a clean Markdown document from structured response fields."""
    try:
        rec_bullets = "\n".join(f"- {item}" for item in (resp.recommendations or []))
        consolidation_block = f"\n## Debt Consolidation Analysis\n{resp.consolidation_analysis}\n" if resp.consolidation_analysis else ""
        
        return f"""# {resp.title or fallback_title}

**Customer ID:** {resp.customer_id}  
**Report Date:** {resp.report_date}  
**Credit Score:** {resp.credit_score}

## Executive Summary
{resp.executive_summary}

## Payment Strategy Analysis
{resp.payment_strategy_analysis}

### Financial Comparison Table
{resp.financial_comparison_table_markdown}

{consolidation_block}## Potential Savings Analysis
{resp.savings_analysis}

## Personalized Recommendations
{rec_bullets}
""".strip()
    except Exception as e:
        logging.error(f"Error assembling markdown from structured response: {e}")
        return f"# {fallback_title}\n\nError generating structured report content."
