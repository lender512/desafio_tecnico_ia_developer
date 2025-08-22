"""
Customer service for retrieving customer information
"""
from typing import List, Optional
from decimal import Decimal
from fastapi import Depends

from ..db.database import MockDatabase, get_db
from ..schemas.customer import (
    CustomerProfile, CustomerSummary
)
from ..schemas.loan import Loan
from ..schemas.card import Card
from ..schemas.payment import Payment
from ..schemas.credit_score import CreditScore
from ..schemas.cashflow import CustomerCashflow


class CustomerService:
    """Service for customer-related operations (read-only)"""

    def __init__(self, db: MockDatabase = Depends(get_db)):
        self.db = db

    def get_customer_profile(self, customer_id: str) -> Optional[CustomerProfile]:
        """Get complete customer profile with all financial data"""
        customer_data = self.db.get_customer_data(customer_id)
        
        # Check if customer exists
        if (customer_data['loans'].empty and 
            customer_data['cards'].empty and 
            customer_data['payments_history'].empty and 
            customer_data['credit_score_history'].empty and 
            customer_data['customer_cashflow'].empty):
            return None

        # Convert DataFrames to schema objects
        loans = [
            Loan(**row.to_dict()) 
            for _, row in customer_data['loans'].iterrows()
        ]
        
        cards = [
            Card(**row.to_dict()) 
            for _, row in customer_data['cards'].iterrows()
        ]
        
        payments_history = [
            Payment(**row.to_dict()) 
            for _, row in customer_data['payments_history'].iterrows()
        ]
        
        credit_scores = [
            CreditScore(**row.to_dict()) 
            for _, row in customer_data['credit_score_history'].iterrows()
        ]
        
        cashflow = None
        if not customer_data['customer_cashflow'].empty:
            cashflow_data = customer_data['customer_cashflow'].iloc[0].to_dict()
            cashflow = CustomerCashflow(**cashflow_data)

        return CustomerProfile(
            customer_id=customer_id,
            loans=loans,
            cards=cards,
            payments_history=payments_history,
            credit_scores=credit_scores,
            cashflow=cashflow
        )

    def get_customer_summary(self, customer_id: str) -> Optional[CustomerSummary]:
        """Get customer financial summary"""
        customer_data = self.db.get_customer_data(customer_id)
        
        # Check if customer exists
        if (customer_data['loans'].empty and 
            customer_data['cards'].empty and 
            customer_data['credit_score_history'].empty):
            return None

        # Calculate total debt
        total_debt = Decimal('0')
        total_monthly_payments = Decimal('0')
        
        # Add loan debt and payments
        for _, loan in customer_data['loans'].iterrows():
            total_debt += Decimal(str(loan['principal']))
            # Calculate monthly payment (simple estimation)
            monthly_rate = Decimal(str(loan['annual_rate_pct'])) / Decimal('100') / Decimal('12')
            term = int(loan['remaining_term_months'])
            if term > 0 and monthly_rate > 0:
                monthly_payment = (Decimal(str(loan['principal'])) * monthly_rate * 
                                 (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
                total_monthly_payments += monthly_payment

        # Add card debt and minimum payments
        for _, card in customer_data['cards'].iterrows():
            balance = Decimal(str(card['balance']))
            total_debt += balance
            min_payment = balance * Decimal(str(card['min_payment_pct'])) / Decimal('100')
            total_monthly_payments += min_payment

        # Get current credit score
        current_credit_score = None
        if not customer_data['credit_score_history'].empty:
            # Get most recent score
            credit_scores = customer_data['credit_score_history'].sort_values('date', ascending=False)
            current_credit_score = int(credit_scores.iloc[0]['credit_score'])

        # Calculate financial health score (simplified)
        financial_health_score = None
        risk_level = None
        if current_credit_score:
            if current_credit_score >= 720:
                financial_health_score = 85
                risk_level = "low"
            elif current_credit_score >= 650:
                financial_health_score = 65
                risk_level = "medium"
            else:
                financial_health_score = 40
                risk_level = "high"

        return CustomerSummary(
            customer_id=customer_id,
            total_debt=total_debt,
            total_monthly_payments=total_monthly_payments,
            current_credit_score=current_credit_score,
            financial_health_score=financial_health_score,
            risk_level=risk_level
        )

    def list_all_customers(self) -> List[str]:
        """Get list of all customer IDs"""
        all_customer_ids = set()
        
        # Collect customer IDs from all tables
        loans_df = self.db.get_loans()
        cards_df = self.db.get_cards()
        payments_df = self.db.get_payments_history()
        credit_df = self.db.get_credit_score_history()
        cashflow_df = self.db.get_customer_cashflow()
        
        for df in [loans_df, cards_df, payments_df, credit_df, cashflow_df]:
            if 'customer_id' in df.columns:
                all_customer_ids.update(df['customer_id'].unique())
        
        return sorted(list(all_customer_ids))

    def customer_exists(self, customer_id: str) -> bool:
        """Check if customer exists in the system"""
        return customer_id in self.list_all_customers()
