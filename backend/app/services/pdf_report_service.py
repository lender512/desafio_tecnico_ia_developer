"""
PDF Report Generation Service using LangChain agents
"""
import io
from typing import Dict, Any, Optional
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY

from langchain.agents import AgentType, initialize_agent, Tool
from langchain.llms.base import LLM
from langchain.memory import ConversationBufferMemory
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel
from pydantic import ConfigDict

from ..schemas.analysis import DebtAnalysisResult
from ..core.config import settings


class ReportAnalysisLLM(LLM):
    """Custom LLM wrapper for Azure AI that focuses on financial analysis reporting."""

    # Allow non-Pydantic types
    model_config = ConfigDict(arbitrary_types_allowed=True, protected_namespaces=())

    azure_ai_client: Optional[AzureAIChatCompletionsModel] = None

    def __init__(self, azure_ai_client: Optional[AzureAIChatCompletionsModel] = None, **kwargs: Any):
        client = azure_ai_client or AzureAIChatCompletionsModel(
            endpoint=settings.AZURE_INFERENCE_ENDPOINT,
            credential=settings.AZURE_INFERENCE_CREDENTIAL,
            model=settings.AZURE_INFERENCE_MODEL,
        )
        object.__setattr__(self, "azure_ai_client", client)
        super().__init__(**kwargs)

    @property
    def _llm_type(self) -> str:
        return "azure_ai_financial_analysis"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        # Helps LangChain cache
        return {
            "endpoint": getattr(self.azure_ai_client, "endpoint", None),
            "model": getattr(self.azure_ai_client, "model", None),
            "_type": self._llm_type,
        }

    def _call(
        self,
        prompt: str,
        stop: Optional[list] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call Azure AI to generate financial analysis text."""
        try:
            response = self.azure_ai_client.invoke(prompt)
            text = getattr(response, "content", None)
            text = text if isinstance(text, str) and text.strip() else str(response)
            # Respect stop tokens client-side if needed
            if stop and text:
                for s in stop:
                    idx = text.find(s)
                    if idx != -1:
                        text = text[:idx]
                        break
            return text
        except Exception as e:
            return f"Error generating analysis: {e}"


class PDFReportService:
    """Service for generating comprehensive PDF reports using LangChain agents."""

    def __init__(self, llm: Optional[ReportAnalysisLLM] = None):
        self.llm = llm or ReportAnalysisLLM()
        self.memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
        self._setup_agent()

    def _setup_agent(self):
        """Setup LangChain agent with financial analysis tools."""
        tools = [
            Tool(
                name="debt_summary_analyzer",
                description="Analyzes debt summary data and creates natural language descriptions of customer's financial situation",
                func=self._analyze_debt_summary,
            ),
            Tool(
                name="payment_strategy_analyzer",
                description="Analyzes payment strategies and provides insights on minimum vs optimized payment approaches",
                func=self._analyze_payment_strategies,
            ),
            Tool(
                name="consolidation_analyzer",
                description="Analyzes consolidation options and provides recommendations on debt consolidation benefits",
                func=self._analyze_consolidation_options,
            ),
            Tool(
                name="savings_calculator",
                description="Calculates and explains potential savings from different financial strategies",
                func=self._calculate_savings_analysis,
            ),
            Tool(
                name="recommendation_generator",
                description="Generates personalized financial recommendations based on the analysis results",
                func=self._generate_recommendations,
            ),
        ]

        self.agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            memory=self.memory,
            verbose=False,
            max_iterations=5,
        )

    def _analyze_debt_summary(self, analysis_data: str) -> str:
        prompt = f"""
You are a financial analyst. Provide a clear summary of the customer's debt situation:

DATA:
{analysis_data}

Focus on:
- Current debt portfolio overview
- Credit score assessment
- Key financial health indicators
- Risks and positives

Write in a professional, accessible tone.
"""
        return self.llm._call(prompt)

    def _analyze_payment_strategies(self, strategy_data: str) -> str:
        prompt = f"""
You are a financial advisor. Analyze these payment strategies:

DATA:
{strategy_data}

Explain:
- How minimum payments behave long-term
- Benefits of the optimized strategy
- Time and interest savings
- Why the optimized approach is more effective

Use educational, customer-friendly language.
"""
        return self.llm._call(prompt)

    def _analyze_consolidation_options(self, consolidation_data: str) -> str:
        prompt = f"""
You are a debt consolidation specialist. Analyze this consolidation option:

DATA:
{consolidation_data}

Cover:
- How consolidation works
- Specific benefits for this customer
- Rate improvements & payment simplification
- Overall financial impact and considerations
"""
        return self.llm._call(prompt)

    def _calculate_savings_analysis(self, savings_data: str) -> str:
        prompt = f"""
You are a financial calculator expert. Break down the savings clearly:

DATA:
{savings_data}

Provide:
- Interest savings
- Time savings (months/years)
- Total financial benefit
- Practical implications and future impact
"""
        return self.llm._call(prompt)

    def _generate_recommendations(self, full_analysis: str) -> str:
        prompt = f"""
You are a personal financial advisor. Provide specific, actionable recommendations:

FULL CONTEXT:
{full_analysis}

Include:
- Primary recommended action
- Step-by-step implementation plan
- Timeline & milestones
- Additional financial health tips
"""
        return self.llm._call(prompt)

    def _prepare_analysis_context(self, analysis: DebtAnalysisResult) -> Dict[str, str]:
        context = {
            "debt_summary": f"""
Customer ID: {analysis.customer_id}
Current Credit Score: {analysis.current_credit_score}
Minimum Payment Strategy: {analysis.minimum_payment_strategy.months} months, ${analysis.minimum_payment_strategy.total_interest:,.2f} total interest
Optimized Payment Strategy: {analysis.optimized_payment_strategy.months} months, ${analysis.optimized_payment_strategy.total_interest:,.2f} total interest
Savings vs Minimum: ${analysis.savings_vs_minimum.interest_saved:,.2f} interest saved, {analysis.savings_vs_minimum.months_saved} months saved
""",
            "payment_strategies": f"""
Minimum Payment:
- Duration: {analysis.minimum_payment_strategy.months} months
- Total Interest: ${analysis.minimum_payment_strategy.total_interest:,.2f}

Optimized Payment:
- Duration: {analysis.optimized_payment_strategy.months} months
- Total Interest: ${analysis.optimized_payment_strategy.total_interest:,.2f}

Comparison:
- Interest Saved: ${analysis.savings_vs_minimum.interest_saved:,.2f}
- Time Saved: {analysis.savings_vs_minimum.months_saved} months
""",
            "consolidation": "",
            "savings": f"""
Optimized vs Minimum Payment:
- Interest Savings: ${analysis.savings_vs_minimum.interest_saved:,.2f}
- Time Savings: {analysis.savings_vs_minimum.months_saved} months
""",
        }

        if getattr(analysis, "consolidation_option", None):
            context["consolidation"] = f"""
Consolidation Option:
- Offer ID: {analysis.consolidation_option.offer_id}
- New Interest Rate: {analysis.consolidation_option.new_rate_pct}%
- Duration: {analysis.consolidation_option.months} months
- Total Interest: ${analysis.consolidation_option.total_interest:,.2f}
- Consolidated Amount: ${analysis.consolidation_option.consolidated_amount:,.2f}

Consolidation vs Minimum:
- Interest Saved: ${analysis.consolidation_savings.vs_minimum.interest_saved:,.2f}
- Time Saved: {analysis.consolidation_savings.vs_minimum.months_saved} months

Consolidation vs Optimized:
- Interest Saved: ${analysis.consolidation_savings.vs_optimized.interest_saved:,.2f}
- Time Saved: {analysis.consolidation_savings.vs_optimized.months_saved} months
"""
        else:
            context["consolidation"] = getattr(analysis, "consolidation_message", "No consolidation options available")

        if getattr(analysis, "consolidation_savings", None):
            context["savings"] += f"""

Consolidation Savings:
vs Minimum:
- Interest Saved: ${analysis.consolidation_savings.vs_minimum.interest_saved:,.2f}
- Time Saved: {analysis.consolidation_savings.vs_minimum.months_saved} months

vs Optimized:
- Interest Saved: ${analysis.consolidation_savings.vs_optimized.interest_saved:,.2f}
- Time Saved: {analysis.consolidation_savings.vs_optimized.months_saved} months
"""
        return context

    def _generate_report_content(self, analysis: DebtAnalysisResult) -> Dict[str, str]:
        context = self._prepare_analysis_context(analysis)
        sections: Dict[str, str] = {}
        try:
            sections["executive_summary"] = self.agent.run(
                f"Create an executive summary based on: {context['debt_summary']}"
            )
            sections["payment_analysis"] = self.agent.run(
                f"Analyze the payment strategies: {context['payment_strategies']}"
            )
            if getattr(analysis, "consolidation_option", None):
                sections["consolidation_analysis"] = self.agent.run(
                    f"Analyze the consolidation option: {context['consolidation']}"
                )
            else:
                sections["consolidation_analysis"] = "No consolidation options are currently available for this customer."
            sections["savings_analysis"] = self.agent.run(
                f"Explain the savings potential: {context['savings']}"
            )

            full_context = f"""
Summary: {context['debt_summary']}
Strategies: {context['payment_strategies']}
Consolidation: {context['consolidation']}
Savings: {context['savings']}
"""
            sections["recommendations"] = self.agent.run(
                f"Give specific recommendations based on the full context: {full_context}"
            )
        except Exception:
            sections = self._generate_fallback_content(analysis)
        return sections

    def _generate_fallback_content(self, analysis: DebtAnalysisResult) -> Dict[str, str]:
        return {
            "executive_summary": (
                f"Financial analysis for customer {analysis.customer_id} with credit score "
                f"{analysis.current_credit_score}. There is potential for optimization."
            ),
            "payment_analysis": (
                f"Minimum strategy: {analysis.minimum_payment_strategy.months} months, "
                f"${analysis.minimum_payment_strategy.total_interest:,.2f} interest. "
                f"Optimized strategy saves ${analysis.savings_vs_minimum.interest_saved:,.2f} "
                f"and {analysis.savings_vs_minimum.months_saved} months."
            ),
            "consolidation_analysis": (
                "Consolidation analysis completed." if getattr(analysis, "consolidation_option", None)
                else "No consolidation options available."
            ),
            "savings_analysis": (
                f"Potential savings of ${analysis.savings_vs_minimum.interest_saved:,.2f} via optimized strategy."
            ),
            "recommendations": "Adopt the optimized payment strategy to maximize savings.",
        }

    def _create_pdf_document(self, analysis: DebtAnalysisResult, content: Dict[str, str]) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=inch, bottomMargin=inch)

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'], fontSize=24, spaceAfter=30, alignment=TA_CENTER)
        heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'], fontSize=16, spaceAfter=12, spaceBefore=20)
        body_style = ParagraphStyle('CustomBody', parent=styles['Normal'], fontSize=11, spaceAfter=12, alignment=TA_JUSTIFY)

        story = []
        story.append(Paragraph("Personal Financial Analysis Report", title_style))
        story.append(Spacer(1, 20))

        header_data = [
            ["Customer ID:", analysis.customer_id],
            ["Report Date:", datetime.now().strftime("%B %d, %Y")],
            ["Credit Score:", str(analysis.current_credit_score)],
        ]
        header_table = Table(header_data, colWidths=[2 * inch, 3 * inch])
        header_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(header_table)
        story.append(Spacer(1, 30))

        story.append(Paragraph("Executive Summary", heading_style))
        story.append(Paragraph(content["executive_summary"], body_style))

        story.append(Paragraph("Payment Strategy Analysis", heading_style))
        story.append(Paragraph(content["payment_analysis"], body_style))

        financial_data = [
            ["Strategy", "Duration (Months)", "Total Interest", "Monthly Payment*"],
            ["Minimum Payment", str(analysis.minimum_payment_strategy.months), f"${analysis.minimum_payment_strategy.total_interest:,.2f}", "Varies"],
            ["Optimized Payment", str(analysis.optimized_payment_strategy.months), f"${analysis.optimized_payment_strategy.total_interest:,.2f}", "Varies"],
        ]
        if getattr(analysis, "consolidation_option", None):
            financial_data.append([
                "Consolidation", str(analysis.consolidation_option.months),
                f"${analysis.consolidation_option.total_interest:,.2f}", "Fixed"
            ])

        financial_table = Table(financial_data, colWidths=[1.5 * inch, 1.2 * inch, 1.5 * inch, 1.3 * inch])
        financial_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(financial_table)
        story.append(Spacer(1, 20))

        story.append(Paragraph("Debt Consolidation Analysis", heading_style))
        story.append(Paragraph(content["consolidation_analysis"], body_style))

        story.append(Paragraph("Potential Savings Analysis", heading_style))
        story.append(Paragraph(content["savings_analysis"], body_style))

        if getattr(analysis, "savings_vs_minimum", None):
            savings_data = [
                ["Comparison", "Interest Saved", "Time Saved (Months)"],
                ["Optimized vs Minimum", f"${analysis.savings_vs_minimum.interest_saved:,.2f}", str(analysis.savings_vs_minimum.months_saved)],
            ]
            if getattr(analysis, "consolidation_savings", None):
                savings_data.extend([
                    ["Consolidation vs Minimum", f"${analysis.consolidation_savings.vs_minimum.interest_saved:,.2f}", str(analysis.consolidation_savings.vs_minimum.months_saved)],
                    ["Consolidation vs Optimized", f"${analysis.consolidation_savings.vs_optimized.interest_saved:,.2f}", str(analysis.consolidation_savings.vs_optimized.months_saved)],
                ])
            savings_table = Table(savings_data, colWidths=[2 * inch, 1.5 * inch, 1.5 * inch])
            savings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(savings_table)
            story.append(Spacer(1, 20))

        story.append(Paragraph("Personalized Recommendations", heading_style))
        story.append(Paragraph(content["recommendations"], body_style))

        story.append(Spacer(1, 30))
        footer_text = "*Monthly payments may vary based on balance and terms. This analysis is for informational purposes only."
        story.append(Paragraph(footer_text, styles['Normal']))

        doc.build(story)
        buffer.seek(0)
        return buffer.getvalue()

    def generate_financial_report(self, analysis: DebtAnalysisResult) -> bytes:
        """Generate a comprehensive PDF financial report using LangChain agents."""
        content = self._generate_report_content(analysis)
        return self._create_pdf_document(analysis, content)

    def generate_simple_report(self, analysis: DebtAnalysisResult, filename: Optional[str] = None) -> str:
        """Generate and save a simple PDF report to /tmp and return its path."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"financial_report_{analysis.customer_id}_{timestamp}.pdf"
        pdf_bytes = self.generate_financial_report(analysis)
        filepath = f"/tmp/{filename}"
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
        return filepath
