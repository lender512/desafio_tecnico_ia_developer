"""LLM utilities and prompt templates for PDF report generation."""

import logging
from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel

from ..core.config import settings
from ..schemas.analysis import DebtAnalysisResult
from ..schemas.pdf_report import MarkdownDoc, HtmlConversion, STRICT_NO_CHATTER_NOTE


def get_llm(temperature: float = 0.7) -> AzureAIChatCompletionsModel:
    """Get configured Azure AI LLM instance."""
    return AzureAIChatCompletionsModel(
        endpoint=settings.AZURE_INFERENCE_ENDPOINT,
        credential=settings.AZURE_INFERENCE_CREDENTIAL,
        model=settings.AZURE_INFERENCE_MODEL,
        temperature=temperature,
        timeout=None,
    )


def generate_analysis_prompt(analysis: DebtAnalysisResult, context: dict) -> str:
    """Generate prompt for financial analysis text generation."""
    return f"""
    You are a professional financial analyst. Generate a comprehensive financial report analysis based on the following data:

    CUSTOMER INFORMATION:
    - Customer ID: {analysis.customer_id}
    - Current Credit Score: {analysis.current_credit_score}

    PAYMENT STRATEGIES:
    - Minimum Payment Strategy: {analysis.minimum_payment_strategy.months} months, ${analysis.minimum_payment_strategy.total_interest:,.2f} total interest
    - Optimized Payment Strategy: {analysis.optimized_payment_strategy.months} months, ${analysis.optimized_payment_strategy.total_interest:,.2f} total interest
    - Savings vs Minimum: ${analysis.savings_vs_minimum.interest_saved:,.2f} interest saved, {analysis.savings_vs_minimum.months_saved} months saved

    CONSOLIDATION INFORMATION:
    {context['consolidation']}

    Please provide a comprehensive analysis covering:
    1. Executive Summary of the customer's financial situation
    2. Detailed Payment Strategy Analysis comparing minimum vs optimized approaches
    3. Debt Consolidation Analysis (if applicable)
    4. Potential Savings Analysis with specific numbers
    5. Personalized Recommendations with actionable steps

    Write in a professional, accessible tone that a customer can understand. Be specific with numbers and timeframes.
    """


def generate_markdown_formatting_prompt(raw_analysis: str, analysis: DebtAnalysisResult) -> str:
    """Generate prompt for formatting analysis into structured markdown."""
    from datetime import datetime
    
    return f"""
    You are formatting a financial analysis into a well-structured Markdown report.
    Return data ONLY via the structured schema provided by the tool—do not include any extra text.

    Requirements:
    - Use proper Markdown headers (#, ##, ###) in the final 'markdown' field if you provide it.
    - Include a valid GitHub-flavored Markdown table in 'financial_comparison_table_markdown'.
    - Format currency with symbols and thousands separators where applicable.
    - Recommendations should be clean bullet items in the 'recommendations' list (no leading '-' or numbering).
    - If you provide the 'markdown' field, it must be a complete report ready to render.

    Context:
    ANALYSIS TEXT:
    {raw_analysis}

    Report fixed values for this customer:
    - Customer ID: {analysis.customer_id}
    - Report Date: {datetime.now().strftime("%B %d, %Y")}
    - Credit Score: {analysis.current_credit_score}

    Report structure (for the 'markdown' field if you choose to include it):
    # Personal Financial Analysis Report

    **Customer ID:** {analysis.customer_id}  
    **Report Date:** {datetime.now().strftime("%B %d, %Y")}  
    **Credit Score:** {analysis.current_credit_score}

    ## Executive Summary
    ...

    ## Payment Strategy Analysis
    ...

    ### Financial Comparison Table
    {{
    financial_comparison_table_markdown
    }}

    ## Debt Consolidation Analysis
    ...

    ## Potential Savings Analysis
    ...

    ## Personalized Recommendations
    - ...
    - ...
    """


def generate_html_conversion_prompt(markdown_content: str) -> str:
    """Generate prompt for converting markdown to HTML."""
    return f"""
    Convert the following Markdown content to clean, semantic HTML.

    {STRICT_NO_CHATTER_NOTE}

    REQUIREMENTS:
    - Convert #/##/### to <h1>/<h2>/<h3>.
    - Convert Markdown tables to HTML tables. Prefer <thead> for the header row and <tbody> for the rest.
    - Convert lists to <ul>/<ol>/<li>, **bold** to <strong>, *italic* to <em>, links to <a>.
    - Preserve paragraphs with <p>.
    - Use only semantic HTML—NO <!DOCTYPE>, <html>, <head>, or <body> tags.

    Return the result ONLY via the structured schema.

    MARKDOWN:
    {markdown_content}
    """


def invoke_llm_for_analysis(llm: AzureAIChatCompletionsModel, prompt: str) -> str:
    """Invoke LLM for analysis text generation with error handling."""
    try:
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content if hasattr(response, 'content') else str(response)
    except Exception as e:
        logging.error(f"Error generating analysis text: {e}")
        raise


def invoke_llm_for_markdown(llm: AzureAIChatCompletionsModel, prompt: str) -> MarkdownDoc:
    """Invoke LLM for structured markdown generation with error handling."""
    try:
        parser = llm.with_structured_output(MarkdownDoc)
        return parser.invoke([HumanMessage(content=prompt)])
    except Exception as e:
        logging.error(f"Error formatting to markdown (structured): {e}")
        raise


def invoke_llm_for_html(llm: AzureAIChatCompletionsModel, prompt: str) -> HtmlConversion:
    """Invoke LLM for HTML conversion with error handling."""
    try:
        parser = llm.with_structured_output(HtmlConversion)
        return parser.invoke([HumanMessage(content=prompt)])
    except Exception as e:
        logging.error(f"Error converting markdown to HTML with LLM (structured): {e}")
        raise
