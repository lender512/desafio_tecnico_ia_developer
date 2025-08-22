import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Any
from decimal import Decimal
from app.services.azure_ai_service import AzureAIService
from fastapi import Depends
import logging

from ..db.database import MockDatabase, get_db
from ..schemas.analysis import (
    ConsolidationOffer,
    PaymentSimulationResult,
    ConsolidationSimulationResult,
    DebtAnalysisResult,
    EligibleOffersResponse,
    SavingsComparison,
    ConsolidationSavings
)


class AnalysisService:
    """Service for financial analysis and restructuring (read-only)"""

    def __init__(self, db: MockDatabase = Depends(get_db), azure_ai_service: AzureAIService = Depends()):
        self.db = db
        self.azure_ai_service = azure_ai_service

    def _convert_to_dict(self, df_row) -> Dict[str, Any]:
        """Convert pandas DataFrame row to dictionary with proper data types"""
        result = {}
        for key, value in df_row.items():
            if isinstance(value, Decimal):
                result[key] = float(value)
            else:
                result[key] = value
        return result

    def _pmt(self, principal: pd.Series, annual_rate_pct: pd.Series, n_months: pd.Series) -> pd.Series:
        """Calculate payment amount for loans using pandas vectorized operations"""
        r = annual_rate_pct / 100 / 12
        # Handle edge cases
        result = pd.Series(index=principal.index, dtype=float)

        # Case 1: n_months <= 0
        mask_zero_months = n_months <= 0
        result.loc[mask_zero_months] = principal.loc[mask_zero_months]

        # Case 2: rate is 0
        mask_zero_rate = (r == 0) & (~mask_zero_months)
        result.loc[mask_zero_rate] = principal.loc[mask_zero_rate] / \
            n_months.loc[mask_zero_rate]

        # Case 3: normal calculation
        mask_normal = (~mask_zero_months) & (~mask_zero_rate)
        if mask_normal.any():
            r_normal = r.loc[mask_normal]
            n_normal = n_months.loc[mask_normal]
            p_normal = principal.loc[mask_normal]

            result.loc[mask_normal] = p_normal * \
                (r_normal * (1 + r_normal)**n_normal) / \
                ((1 + r_normal)**n_normal - 1)

        return result

    def _check_eligibility_with_ai(self, customer_data: Dict, offer: ConsolidationOffer, credit_score: int) -> bool:
        """
        Check offer eligibility using pandas logic for basic criteria and AI only for natural language conditions
        """
        # First, apply basic eligibility checks using pandas logic
        basic_eligible = self._check_basic_eligibility(
            customer_data, offer, credit_score)
        if not basic_eligible:
            return False

        # If basic checks pass and there are natural language conditions, use AI to evaluate them
        if offer.conditions and offer.conditions.strip() and offer.conditions.lower() not in ['none', 'none specified', '']:
            return self._evaluate_conditions_with_ai(customer_data, offer, credit_score)

        # If no specific conditions or conditions are empty, customer is eligible
        return True

    def _check_basic_eligibility(self, customer_data: Dict, offer: ConsolidationOffer) -> bool:
        """
        Check basic eligibility criteria using pandas logic
        """
        # Check if customer has eligible product types for consolidation
        loans_df = customer_data['loans']
        cards_df = customer_data['cards']
        types_eligible = set(offer.product_types_eligible)

        eligible_debt = 0.0
        if not loans_df.empty:
            eligible_loans = loans_df[loans_df['product_type'].isin(
                types_eligible)]
            eligible_debt += eligible_loans['principal'].sum()

        if not cards_df.empty and "card" in types_eligible:
            eligible_debt += cards_df['balance'].sum()

        # Check if there's enough eligible debt and it doesn't exceed the offer limit
        if eligible_debt <= 0:
            logging.info(
                f"No eligible debt for consolidation in offer {offer.offer_id}")
            return False

        # Check if eligible debt exceeds max consolidated balance
        if eligible_debt > offer.max_consolidated_balance:
            logging.info(
                f"Eligible debt {eligible_debt} exceeds max consolidated balance for offer {offer.offer_id}")
            return False

        # Check max term months
        if offer.max_term_months < loans_df['remaining_term_months'].max():
            logging.info(
                f"Max term months {offer.max_term_months} exceeded for offer {offer.offer_id}")
            return False

        return True

    def _evaluate_conditions_with_ai(self, customer_data: Dict, offer: ConsolidationOffer, credit_score: int) -> bool:
        """
        Use Azure AI to evaluate natural language conditions only
        """
        # Prepare customer profile for AI analysis
        customer_profile = {
            "credit_score": credit_score,
            "max_days_past_due": self._get_max_dpd(customer_data),
            "has_active_delinquency": self._has_active_dpd(customer_data),
            "total_debt": self._calculate_total_debt(customer_data),
            "debt_to_income_ratio": self._calculate_debt_to_income(customer_data),
            "payment_history": self._get_payment_history_summary(customer_data)
        }

        # Delegate to Azure AI service
        return self.azure_ai_service.evaluate_consolidation_conditions(customer_profile, offer)

    def _get_max_dpd(self, customer_data: Dict) -> int:
        """Get maximum days past due across all debts"""
        all_dpds = []

        loans_df = customer_data['loans']
        cards_df = customer_data['cards']

        if not loans_df.empty:
            all_dpds.extend(loans_df['days_past_due'].tolist())
        if not cards_df.empty:
            all_dpds.extend(cards_df['days_past_due'].tolist())

        return max(all_dpds) if all_dpds else 0

    def _has_active_dpd(self, customer_data: Dict) -> bool:
        """Check if customer has any active delinquency"""
        loans_df = customer_data['loans']
        cards_df = customer_data['cards']

        loans_dpd = loans_df['days_past_due'].gt(
            0).any() if not loans_df.empty else False
        cards_dpd = cards_df['days_past_due'].gt(
            0).any() if not cards_df.empty else False

        return loans_dpd or cards_dpd

    def _calculate_total_debt(self, customer_data: Dict) -> float:
        """Calculate total debt across loans and cards"""
        total = 0.0

        loans_df = customer_data['loans']
        cards_df = customer_data['cards']

        if not loans_df.empty:
            total += loans_df['principal'].sum()
        if not cards_df.empty:
            total += cards_df['balance'].sum()

        return float(total)

    def _calculate_debt_to_income(self, customer_data: Dict) -> float:
        """Calculate debt-to-income ratio"""
        cashflow_df = customer_data['customer_cashflow']
        if cashflow_df.empty:
            return 0.0

        monthly_income = float(cashflow_df.iloc[0]['monthly_income_avg'])
        total_debt = self._calculate_total_debt(customer_data)

        return total_debt / (monthly_income * 12) if monthly_income > 0 else 0.0

    def _get_payment_history_summary(self, customer_data: Dict) -> Dict:
        """Get payment history summary"""
        loans_df = customer_data['loans']
        cards_df = customer_data['cards']

        total_accounts = len(loans_df) + len(cards_df)
        delinquent_accounts = 0

        if not loans_df.empty:
            delinquent_accounts += loans_df['days_past_due'].gt(0).sum()
        if not cards_df.empty:
            delinquent_accounts += cards_df['days_past_due'].gt(0).sum()

        return {
            "total_accounts": total_accounts,
            "delinquent_accounts": int(delinquent_accounts),
            "delinquency_rate": delinquent_accounts / total_accounts if total_accounts > 0 else 0.0
        }

    def simulate_minimum_payments(self, customer_id: str) -> PaymentSimulationResult:
        """
        Simulate minimum payment strategy for a customer
        Returns months to payoff and total interest paid
        """
        customer_data = self.db.get_customer_data(customer_id)

        # Work directly with DataFrames for better performance
        loans_df = customer_data['loans'].copy()
        cards_df = customer_data['cards'].copy()

        total_interest, months = 0.0, 0

        # Convert to float for calculations
        if not loans_df.empty:
            loans_df['principal'] = loans_df['principal'].astype(float)
            loans_df['annual_rate_pct'] = loans_df['annual_rate_pct'].astype(
                float)
            loans_df['remaining_term_months'] = loans_df['remaining_term_months'].astype(
                int)

        if not cards_df.empty:
            cards_df['balance'] = cards_df['balance'].astype(float)
            cards_df['annual_rate_pct'] = cards_df['annual_rate_pct'].astype(
                float)
            cards_df['min_payment_pct'] = cards_df['min_payment_pct'].astype(
                float)

        def done():
            loans_done = loans_df.empty or (
                loans_df['principal'] <= 1e-6).all()
            cards_done = cards_df.empty or (cards_df['balance'] <= 1e-6).all()
            return loans_done and cards_done

        while not done() and months < 1000:
            months += 1

            # Process loans using pandas operations
            if not loans_df.empty:
                active_loans = loans_df['principal'] > 1e-6
                if active_loans.any():
                    # Calculate monthly interest
                    monthly_rates = loans_df.loc[active_loans,
                                                 'annual_rate_pct'] / 100 / 12
                    interest = loans_df.loc[active_loans,
                                            'principal'] * monthly_rates
                    total_interest += interest.sum()

                    # Calculate payments
                    payments = self._pmt(
                        loans_df.loc[active_loans, 'principal'],
                        loans_df.loc[active_loans, 'annual_rate_pct'],
                        loans_df.loc[active_loans,
                                     'remaining_term_months'].clip(lower=1)
                    )

                    # Calculate payoffs and principal reductions
                    payoffs = loans_df.loc[active_loans,
                                           'principal'] + interest
                    actual_payments = np.minimum(payments, payoffs)
                    principal_reductions = actual_payments - interest

                    # Update principals and terms
                    loans_df.loc[active_loans, 'principal'] = np.maximum(
                        0.0, loans_df.loc[active_loans,
                                          'principal'] - principal_reductions
                    )
                    loans_df.loc[active_loans, 'remaining_term_months'] = np.maximum(
                        1, loans_df.loc[active_loans,
                                        'remaining_term_months'] - 1
                    )

            # Process cards using pandas operations
            if not cards_df.empty:
                active_cards = cards_df['balance'] > 1e-6
                if active_cards.any():
                    # Calculate monthly interest
                    monthly_rates = cards_df.loc[active_cards,
                                                 'annual_rate_pct'] / 100 / 12
                    interest = cards_df.loc[active_cards,
                                            'balance'] * monthly_rates
                    total_interest += interest.sum()

                    # Calculate minimum payments
                    min_payments = np.maximum(
                        cards_df.loc[active_cards, 'balance'] *
                        (cards_df.loc[active_cards, 'min_payment_pct'] / 100),
                        interest + 1.0
                    )

                    # Calculate payoffs and principal reductions
                    payoffs = cards_df.loc[active_cards, 'balance'] + interest
                    actual_payments = np.minimum(min_payments, payoffs)
                    principal_reductions = actual_payments - interest

                    # Update balances
                    cards_df.loc[active_cards, 'balance'] = np.maximum(
                        0.0, cards_df.loc[active_cards,
                                          'balance'] - principal_reductions
                    )

        return PaymentSimulationResult(
            months=months,
            total_interest=total_interest
        )

    def simulate_optimized_payments(self, customer_id: str, cure_dpd_first: bool = True) -> PaymentSimulationResult:
        """
        Simulate optimized payment strategy (avalanche method)
        Returns months to payoff and total interest paid
        """
        customer_data = self.db.get_customer_data(customer_id)

        if customer_data['customer_cashflow'].empty:
            raise ValueError(
                f"No cashflow data found for customer {customer_id}")

        # Get cashflow data
        cashflow_row = customer_data['customer_cashflow'].iloc[0]
        income = float(cashflow_row['monthly_income_avg'])
        essential = float(cashflow_row['essential_expenses_avg'])
        variability = float(cashflow_row['income_variability_pct']) / 100
        budget = max(0.0, income - essential - income * variability)

        # Work with DataFrames
        loans_df = customer_data['loans'].copy()
        cards_df = customer_data['cards'].copy()

        # Convert to float for calculations
        if not loans_df.empty:
            loans_df['principal'] = loans_df['principal'].astype(float)
            loans_df['annual_rate_pct'] = loans_df['annual_rate_pct'].astype(
                float)
            loans_df['remaining_term_months'] = loans_df['remaining_term_months'].astype(
                int)
            loans_df['days_past_due'] = loans_df['days_past_due'].astype(int)

        if not cards_df.empty:
            cards_df['balance'] = cards_df['balance'].astype(float)
            cards_df['annual_rate_pct'] = cards_df['annual_rate_pct'].astype(
                float)
            cards_df['min_payment_pct'] = cards_df['min_payment_pct'].astype(
                float)
            cards_df['days_past_due'] = cards_df['days_past_due'].astype(int)

        total_interest, months = 0.0, 0

        def calculate_minimum_payments():
            """Calculate minimum payments for all active debts"""
            total_min = 0.0
            loan_payments = pd.Series(dtype=float)
            card_payments = pd.Series(dtype=float)

            if not loans_df.empty:
                active_loans = loans_df['principal'] > 1e-6
                if active_loans.any():
                    loan_payments = self._pmt(
                        loans_df.loc[active_loans, 'principal'],
                        loans_df.loc[active_loans, 'annual_rate_pct'],
                        loans_df.loc[active_loans,
                                     'remaining_term_months'].clip(lower=1)
                    )
                    total_min += loan_payments.sum()

            if not cards_df.empty:
                active_cards = cards_df['balance'] > 1e-6
                if active_cards.any():
                    monthly_rates = cards_df.loc[active_cards,
                                                 'annual_rate_pct'] / 100 / 12
                    interest = cards_df.loc[active_cards,
                                            'balance'] * monthly_rates
                    card_payments = np.maximum(
                        cards_df.loc[active_cards, 'balance'] *
                        (cards_df.loc[active_cards, 'min_payment_pct'] / 100),
                        interest + 1.0
                    )
                    total_min += card_payments.sum()

            return total_min, loan_payments, card_payments

        def get_priority_debt():
            """Get the highest priority debt for extra payments"""
            debts = []

            # Add loans
            if not loans_df.empty:
                active_loans = loans_df['principal'] > 1e-6
                for idx in loans_df[active_loans].index:
                    loan = loans_df.loc[idx]
                    priority = (
                        0 if (
                            cure_dpd_first and loan['days_past_due'] > 0) else 1,
                        # Negative for descending sort
                        -loan['annual_rate_pct']
                    )
                    debts.append((priority, 'loan', idx, loan['principal']))

            # Add cards
            if not cards_df.empty:
                active_cards = cards_df['balance'] > 1e-6
                for idx in cards_df[active_cards].index:
                    card = cards_df.loc[idx]
                    priority = (
                        0 if (
                            cure_dpd_first and card['days_past_due'] > 0) else 1,
                        # Negative for descending sort
                        -card['annual_rate_pct']
                    )
                    debts.append((priority, 'card', idx, card['balance']))

            if not debts:
                return None

            debts.sort()
            return debts[0]

        def done():
            loans_done = loans_df.empty or (
                loans_df['principal'] <= 1e-6).all()
            cards_done = cards_df.empty or (cards_df['balance'] <= 1e-6).all()
            return loans_done and cards_done

        while not done() and months < 1000:
            months += 1

            # Calculate monthly interest
            if not loans_df.empty:
                active_loans = loans_df['principal'] > 1e-6
                if active_loans.any():
                    monthly_rates = loans_df.loc[active_loans,
                                                 'annual_rate_pct'] / 100 / 12
                    interest = loans_df.loc[active_loans,
                                            'principal'] * monthly_rates
                    total_interest += interest.sum()

            if not cards_df.empty:
                active_cards = cards_df['balance'] > 1e-6
                if active_cards.any():
                    monthly_rates = cards_df.loc[active_cards,
                                                 'annual_rate_pct'] / 100 / 12
                    interest = cards_df.loc[active_cards,
                                            'balance'] * monthly_rates
                    total_interest += interest.sum()

            # Calculate minimum payments
            mins_total, loan_payments, card_payments = calculate_minimum_payments()
            extra = max(0.0, budget - mins_total)

            # Apply minimum payments to loans
            if not loan_payments.empty:
                for idx, payment in loan_payments.items():
                    if loans_df.loc[idx, 'principal'] > 1e-6:
                        monthly_rate = loans_df.loc[idx,
                                                    'annual_rate_pct'] / 100 / 12
                        interest = loans_df.loc[idx,
                                                'principal'] * monthly_rate
                        payoff = loans_df.loc[idx, 'principal'] + interest
                        actual_payment = min(payment, payoff)
                        principal_reduction = actual_payment - interest

                        loans_df.loc[idx, 'principal'] = max(
                            0.0, loans_df.loc[idx, 'principal'] - principal_reduction)
                        loans_df.loc[idx, 'remaining_term_months'] = max(
                            1, loans_df.loc[idx, 'remaining_term_months'] - 1)

            # Apply minimum payments to cards
            if not card_payments.empty:
                for idx, payment in card_payments.items():
                    if cards_df.loc[idx, 'balance'] > 1e-6:
                        monthly_rate = cards_df.loc[idx,
                                                    'annual_rate_pct'] / 100 / 12
                        interest = cards_df.loc[idx, 'balance'] * monthly_rate
                        payoff = cards_df.loc[idx, 'balance'] + interest
                        actual_payment = min(payment, payoff)
                        principal_reduction = actual_payment - interest

                        cards_df.loc[idx, 'balance'] = max(
                            0.0, cards_df.loc[idx, 'balance'] - principal_reduction)

            # Apply extra payment using avalanche method
            if extra > 1e-6:
                priority_debt = get_priority_debt()
                if priority_debt:
                    _, debt_type, idx, current_balance = priority_debt
                    if debt_type == "loan":
                        payment = min(extra, loans_df.loc[idx, 'principal'])
                        loans_df.loc[idx, 'principal'] = max(
                            0.0, loans_df.loc[idx, 'principal'] - payment)
                    else:  # card
                        payment = min(extra, cards_df.loc[idx, 'balance'])
                        cards_df.loc[idx, 'balance'] = max(
                            0.0, cards_df.loc[idx, 'balance'] - payment)

        return PaymentSimulationResult(
            months=months,
            total_interest=total_interest
        )

    def get_eligible_offers(self, customer_id: str, offers: List[ConsolidationOffer], credit_score: int) -> EligibleOffersResponse:
        """
        Get eligible consolidation offers for a customer using pandas logic for basic criteria
        and Azure AI only for natural language conditions
        """
        customer_data = self.db.get_customer_data(customer_id)

        logging.info(
            f"Starting eligibility check for customer {customer_id} with {len(offers)} offers")

        eligible = []
        ai_used_count = 0

        for offer in offers:
            try:
                # Use the refactored eligibility checking method
                is_eligible = self._check_eligibility_with_ai(
                    customer_data, offer, credit_score)

                # Count AI usage only if there were conditions to evaluate
                if offer.conditions and offer.conditions.strip() and offer.conditions.lower() not in ['none', 'none specified', '']:
                    ai_used_count += 1

                if is_eligible:
                    eligible.append(offer)
                    logging.info(
                        f"Offer {offer.offer_id} approved for customer {customer_id}")
                else:
                    logging.info(
                        f"Offer {offer.offer_id} rejected for customer {customer_id}")

            except Exception as e:
                logging.error(f"Error evaluating offer {offer.offer_id}: {e}")
                # Skip this offer if there's an error in evaluation
                continue

        # Sort by rate (lowest first) - prioritize customer benefit
        eligible_sorted = sorted(eligible, key=lambda x: x.new_rate_pct)

        logging.info(f"Eligibility assessment complete: {len(eligible_sorted)}/{len(offers)} offers eligible. "
                     f"AI evaluations used: {ai_used_count}")

        return EligibleOffersResponse(
            customer_id=customer_id,
            credit_score=credit_score,
            eligible_offers=eligible_sorted,
            total_offers_evaluated=len(offers)
        )

    def simulate_consolidation(self, customer_id: str, offers: List[ConsolidationOffer], credit_score: int) -> Optional[ConsolidationSimulationResult]:
        """
        Simulate debt consolidation for a customer using pandas operations
        Returns consolidation analysis or None if no eligible offers
        """
        customer_data = self.db.get_customer_data(customer_id)

        if customer_data['customer_cashflow'].empty:
            raise ValueError(
                f"No cashflow data found for customer {customer_id}")

        # Get cashflow data
        cashflow_row = customer_data['customer_cashflow'].iloc[0]
        income = float(cashflow_row['monthly_income_avg'])
        essential = float(cashflow_row['essential_expenses_avg'])
        variability = float(cashflow_row['income_variability_pct']) / 100
        budget = max(0.0, income - essential - income * variability)

        eligible_offers_response = self.get_eligible_offers(
            customer_id, offers, credit_score)
        if not eligible_offers_response.eligible_offers:
            return None

        # Best offer (lowest rate)
        offer = eligible_offers_response.eligible_offers[0]
        types_eligible = set(offer.product_types_eligible)

        # Use pandas operations to calculate consolidation amounts
        loans_df = customer_data['loans'].copy()
        cards_df = customer_data['cards'].copy()

        consolidated_amount = 0.0
        remaining_loans_list = []
        remaining_cards_list = []

        # Process loans
        if not loans_df.empty:
            consolidate_loans = loans_df['product_type'].isin(types_eligible)
            consolidated_amount += loans_df.loc[consolidate_loans,
                                                'principal'].sum()

            # Convert remaining loans to list of dicts
            remaining_loans = loans_df.loc[~consolidate_loans]
            remaining_loans_list = [self._convert_to_dict(
                row) for _, row in remaining_loans.iterrows()]

        # Process cards
        if not cards_df.empty and "card" in types_eligible:
            consolidated_amount += cards_df['balance'].sum()
        elif not cards_df.empty:
            # All cards remain if not eligible for consolidation
            remaining_cards_list = [self._convert_to_dict(
                row) for _, row in cards_df.iterrows()]

        consolidated_amount = min(
            consolidated_amount, offer.max_consolidated_balance)
        if consolidated_amount <= 0:
            return None

        # Create new consolidation loan
        new_loan = {
            "loan_id": f"CONS-{offer.offer_id}-{customer_id}",
            "customer_id": customer_id,
            "product_type": "consolidation",
            "principal": consolidated_amount,
            "annual_rate_pct": offer.new_rate_pct,
            "remaining_term_months": offer.max_term_months,
            "collateral": False,
            "days_past_due": 0
        }

        # Simulate payment with new loan structure using simplified logic
        all_loans = [new_loan] + remaining_loans_list
        all_cards = remaining_cards_list

        # Create DataFrames for simulation
        sim_loans_df = pd.DataFrame(all_loans) if all_loans else pd.DataFrame()
        sim_cards_df = pd.DataFrame(all_cards) if all_cards else pd.DataFrame()

        # Convert to proper dtypes if not empty
        if not sim_loans_df.empty:
            sim_loans_df['principal'] = sim_loans_df['principal'].astype(float)
            sim_loans_df['annual_rate_pct'] = sim_loans_df['annual_rate_pct'].astype(
                float)
            sim_loans_df['remaining_term_months'] = sim_loans_df['remaining_term_months'].astype(
                int)

        if not sim_cards_df.empty:
            sim_cards_df['balance'] = sim_cards_df['balance'].astype(float)
            sim_cards_df['annual_rate_pct'] = sim_cards_df['annual_rate_pct'].astype(
                float)
            sim_cards_df['min_payment_pct'] = sim_cards_df['min_payment_pct'].astype(
                float)

        total_interest, months = 0.0, 0

        def done():
            loans_done = sim_loans_df.empty or (
                sim_loans_df['principal'] <= 1e-6).all()
            cards_done = sim_cards_df.empty or (
                sim_cards_df['balance'] <= 1e-6).all()
            return loans_done and cards_done

        while not done() and months < 1000:
            months += 1

            # Calculate monthly interest
            monthly_interest = 0.0
            if not sim_loans_df.empty:
                active_loans = sim_loans_df['principal'] > 1e-6
                if active_loans.any():
                    loan_interest = (sim_loans_df.loc[active_loans, 'principal'] *
                                     sim_loans_df.loc[active_loans, 'annual_rate_pct'] / 100 / 12)
                    monthly_interest += loan_interest.sum()

            if not sim_cards_df.empty:
                active_cards = sim_cards_df['balance'] > 1e-6
                if active_cards.any():
                    card_interest = (sim_cards_df.loc[active_cards, 'balance'] *
                                     sim_cards_df.loc[active_cards, 'annual_rate_pct'] / 100 / 12)
                    monthly_interest += card_interest.sum()

            total_interest += monthly_interest

            # Calculate minimum payments needed
            total_min_needed = 0.0
            if not sim_loans_df.empty:
                active_loans = sim_loans_df['principal'] > 1e-6
                if active_loans.any():
                    loan_payments = self._pmt(
                        sim_loans_df.loc[active_loans, 'principal'],
                        sim_loans_df.loc[active_loans, 'annual_rate_pct'],
                        sim_loans_df.loc[active_loans,
                                         'remaining_term_months'].clip(lower=1)
                    )
                    total_min_needed += loan_payments.sum()

            if not sim_cards_df.empty:
                active_cards = sim_cards_df['balance'] > 1e-6
                if active_cards.any():
                    card_interest = (sim_cards_df.loc[active_cards, 'balance'] *
                                     sim_cards_df.loc[active_cards, 'annual_rate_pct'] / 100 / 12)
                    min_card_payments = np.maximum(
                        sim_cards_df.loc[active_cards, 'balance'] *
                        (sim_cards_df.loc[active_cards,
                         'min_payment_pct'] / 100),
                        card_interest + 1.0
                    )
                    total_min_needed += min_card_payments.sum()

            if budget < total_min_needed:
                # Cannot afford minimum payments, break
                break

            # Apply payments - simplified approach: pay minimums then extra to highest rate
            available_budget = budget

            # Pay loan minimums
            if not sim_loans_df.empty:
                active_loans = sim_loans_df['principal'] > 1e-6
                for idx in sim_loans_df[active_loans].index:
                    principal = sim_loans_df.loc[idx, 'principal']
                    rate = sim_loans_df.loc[idx, 'annual_rate_pct']
                    term = max(
                        1, sim_loans_df.loc[idx, 'remaining_term_months'])

                    min_payment = self._pmt(pd.Series([principal]), pd.Series(
                        [rate]), pd.Series([term])).iloc[0]
                    interest = principal * rate / 100 / 12
                    principal_payment = min(min_payment - interest, principal)

                    sim_loans_df.loc[idx, 'principal'] = max(
                        0.0, principal - principal_payment)
                    sim_loans_df.loc[idx, 'remaining_term_months'] = max(
                        1, term - 1)
                    available_budget -= min_payment

            # Pay card minimums
            if not sim_cards_df.empty:
                active_cards = sim_cards_df['balance'] > 1e-6
                for idx in sim_cards_df[active_cards].index:
                    balance = sim_cards_df.loc[idx, 'balance']
                    rate = sim_cards_df.loc[idx, 'annual_rate_pct']
                    min_pct = sim_cards_df.loc[idx, 'min_payment_pct']

                    interest = balance * rate / 100 / 12
                    min_payment = max(balance * min_pct / 100, interest + 1.0)
                    principal_payment = min(min_payment - interest, balance)

                    sim_cards_df.loc[idx, 'balance'] = max(
                        0.0, balance - principal_payment)
                    available_budget -= min_payment

            # Apply extra to highest rate debt
            if available_budget > 1e-6:
                all_debts = []

                # Add loans
                if not sim_loans_df.empty:
                    active_loans = sim_loans_df['principal'] > 1e-6
                    for idx in sim_loans_df[active_loans].index:
                        all_debts.append(
                            (sim_loans_df.loc[idx, 'annual_rate_pct'], 'loan', idx))

                # Add cards
                if not sim_cards_df.empty:
                    active_cards = sim_cards_df['balance'] > 1e-6
                    for idx in sim_cards_df[active_cards].index:
                        all_debts.append(
                            (sim_cards_df.loc[idx, 'annual_rate_pct'], 'card', idx))

                if all_debts:
                    # Sort by rate (highest first)
                    all_debts.sort(reverse=True)
                    rate, debt_type, idx = all_debts[0]

                    if debt_type == 'loan':
                        payment = min(available_budget,
                                      sim_loans_df.loc[idx, 'principal'])
                        sim_loans_df.loc[idx, 'principal'] = max(
                            0.0, sim_loans_df.loc[idx, 'principal'] - payment)
                    else:  # card
                        payment = min(available_budget,
                                      sim_cards_df.loc[idx, 'balance'])
                        sim_cards_df.loc[idx, 'balance'] = max(
                            0.0, sim_cards_df.loc[idx, 'balance'] - payment)

        return ConsolidationSimulationResult(
            offer_id=offer.offer_id,
            months=months,
            total_interest=total_interest,
            new_rate_pct=offer.new_rate_pct,
            max_term_months=offer.max_term_months,
            consolidated_amount=consolidated_amount
        )

    def analyze_customer_debt(self, customer_id: str, consolidation_offers: List[ConsolidationOffer] = None) -> DebtAnalysisResult:
        """
        Comprehensive debt analysis for a customer including minimum payments, 
        optimized payments, and consolidation options
        """
        # Get current credit score
        customer_data = self.db.get_customer_data(customer_id)
        if customer_data['credit_score_history'].empty:
            raise ValueError(
                f"No credit score data found for customer {customer_id}")

        latest_score = customer_data['credit_score_history'].iloc[-1]['credit_score']

        # Run simulations
        min_result = self.simulate_minimum_payments(customer_id)
        opt_result = self.simulate_optimized_payments(customer_id)

        # Calculate savings vs minimum
        savings_vs_min = SavingsComparison(
            interest_saved=min_result.total_interest - opt_result.total_interest,
            months_saved=min_result.months - opt_result.months
        )

        # Initialize analysis result
        analysis = DebtAnalysisResult(
            customer_id=customer_id,
            current_credit_score=latest_score,
            minimum_payment_strategy=min_result,
            optimized_payment_strategy=opt_result,
            savings_vs_minimum=savings_vs_min
        )

        # Add consolidation analysis if offers provided
        if consolidation_offers:
            consolidation_result = self.simulate_consolidation(
                customer_id, consolidation_offers, latest_score)
            if consolidation_result:
                analysis.consolidation_option = consolidation_result
                analysis.consolidation_savings = ConsolidationSavings(
                    vs_minimum=SavingsComparison(
                        interest_saved=min_result.total_interest - consolidation_result.total_interest,
                        months_saved=min_result.months - consolidation_result.months
                    ),
                    vs_optimized=SavingsComparison(
                        interest_saved=opt_result.total_interest - consolidation_result.total_interest,
                        months_saved=opt_result.months - consolidation_result.months
                    )
                )
            else:
                analysis.consolidation_message = "No eligible consolidation offers available"

        return analysis


