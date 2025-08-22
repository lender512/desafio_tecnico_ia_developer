import logging
from typing import Dict, Optional
from fastapi import HTTPException
from pydantic import BaseModel, Field
from langchain_azure_ai.chat_models import AzureAIChatCompletionsModel

from ..core.config import settings
from ..schemas.analysis import ConsolidationOffer


class AzureAIService:
    """Service for Azure AI operations"""

    def __init__(self):
        self.azure_ai_manager = None
        self._init_azure_ai()

    def _init_azure_ai(self):
        """Initialize Azure AI manager if credentials are available"""
        try:
            if settings.AZURE_INFERENCE_ENDPOINT and settings.AZURE_INFERENCE_CREDENTIAL:
                logging.info("Initializing Azure AI manager...")
                self.azure_ai_manager = AzureAIChatCompletionsModel(
                    endpoint=settings.AZURE_INFERENCE_ENDPOINT,
                    credential=settings.AZURE_INFERENCE_CREDENTIAL,
                    model=settings.AZURE_INFERENCE_MODEL,
                )
                logging.info("Azure AI manager initialized successfully")
            else:
                logging.warning("Azure AI credentials not provided")
        except Exception as e:
            logging.error(f"Failed to initialize Azure AI manager: {e}")
            raise HTTPException(
                status_code=500, detail="AI manager initialization failed")

    def is_available(self) -> bool:
        """Check if Azure AI service is available"""
        return self.azure_ai_manager is not None

    def evaluate_consolidation_conditions(self, customer_profile: Dict, offer: ConsolidationOffer) -> bool:
        """
        Use Azure AI to evaluate natural language conditions for consolidation offers
        
        Args:
            customer_profile: Dictionary with customer financial profile
            offer: ConsolidationOffer with conditions to evaluate
            
        Returns:
            bool: True if customer meets the conditions, False otherwise
        """
        if not self.azure_ai_manager:
            logging.warning(
                "AI manager not initialized, skipping conditions evaluation")
            return True  # Default to eligible if AI not available

        # Skip evaluation if no meaningful conditions
        if not offer.conditions or offer.conditions.strip() == "" or offer.conditions.lower() in ['none', 'none specified']:
            return True

        try:
            # Create focused prompt for AI analysis of conditions only
            prompt = f"""
            Evaluate if this customer meets the specific conditions for this consolidation offer.

            Customer Profile:
            - Credit Score: {customer_profile['credit_score']}
            - Maximum Days Past Due: {customer_profile['max_days_past_due']}
            - Has Active Delinquency: {customer_profile['has_active_delinquency']}
            - Total Debt: ${customer_profile['total_debt']:,.2f}
            - Debt-to-Income Ratio: {customer_profile['debt_to_income_ratio']:.2%}
            - Payment History: {customer_profile['payment_history']}
            
            Specific Conditions to Evaluate: {offer.conditions}
            """

            class ConditionEvaluationResponse(BaseModel):
                meets_conditions: bool = Field(
                    description="Does the customer meet the specific conditions?")
                reasoning: str = Field(
                    description="Brief explanation of the decision")

            # Get AI response
            model = self.azure_ai_manager.with_structured_output(
                schema=ConditionEvaluationResponse)
            response = model.invoke(prompt)
            
            logging.info(
                f"AI conditions evaluation for offer {offer.offer_id}: {response.reasoning}")
            return response.meets_conditions

        except Exception as e:
            logging.error(f"Error in AI conditions evaluation: {e}")
            return False  # Default to not eligible if AI evaluation fails
