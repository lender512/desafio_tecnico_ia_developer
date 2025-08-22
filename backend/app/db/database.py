from typing import Generator
import pandas as pd


class MockDatabase:
    """
    Mockup database class with hardcoded data as pandas DataFrames
    """

    def __init__(self):
        """Initialize database with hardcoded data"""
        self._init_dataframes()

    def _init_dataframes(self):
        """Initialize all DataFrames from hardcoded list of dicts"""

        # Loans data
        loans_data = [
            {"loan_id": "L-101", "customer_id": "CU-001", "product_type": "personal", "principal": 18000.00,
             "annual_rate_pct": 28.5, "remaining_term_months": 36, "collateral": False, "days_past_due": 0},
            {"loan_id": "L-102", "customer_id": "CU-002", "product_type": "micro", "principal": 5000.00,
             "annual_rate_pct": 35.0, "remaining_term_months": 24, "collateral": False, "days_past_due": 15},
            {"loan_id": "L-103", "customer_id": "CU-003", "product_type": "personal", "principal": 25000.00,
             "annual_rate_pct": 32.0, "remaining_term_months": 48, "collateral": True, "days_past_due": 7},
        ]
        self._loans_df = pd.DataFrame(loans_data)

        # Cards data
        cards_data = [
            {"card_id": "C-201", "customer_id": "CU-001", "balance": 3500.00, "annual_rate_pct": 45.0,
             "min_payment_pct": 5.0, "payment_due_day": 15, "days_past_due": 0},
            {"card_id": "C-202", "customer_id": "CU-002", "balance": 1200.00, "annual_rate_pct": 39.9,
             "min_payment_pct": 4.0, "payment_due_day": 10, "days_past_due": 5},
            {"card_id": "C-203", "customer_id": "CU-003", "balance": 4800.00, "annual_rate_pct": 42.5,
             "min_payment_pct": 4.5, "payment_due_day": 25, "days_past_due": 2},
        ]
        self._cards_df = pd.DataFrame(cards_data)

        # Payments history data
        payments_history_data = [
            {"product_id": "L-101", "product_type": "loan", "customer_id": "CU-001",
             "date": "2024-03-01", "amount": 600.00},
            {"product_id": "C-201", "product_type": "card", "customer_id": "CU-001",
             "date": "2024-03-05", "amount": 200.00},
            {"product_id": "L-103", "product_type": "loan", "customer_id": "CU-003",
             "date": "2024-02-15", "amount": 850.00},
            {"product_id": "C-203", "product_type": "card", "customer_id": "CU-003",
             "date": "2024-02-25", "amount": 240.00},
            {"product_id": "L-103", "product_type": "loan", "customer_id": "CU-003",
             "date": "2024-03-15", "amount": 850.00},
        ]
        self._payments_history_df = pd.DataFrame(payments_history_data)

        # Credit score history data
        credit_score_history_data = [
            {"customer_id": "CU-001", "date": "2024-03-01", "credit_score": 720},
            {"customer_id": "CU-002", "date": "2024-03-01", "credit_score": 650},
            {"customer_id": "CU-003", "date": "2024-01-01", "credit_score": 680},
            {"customer_id": "CU-003", "date": "2024-02-01", "credit_score": 675},
            {"customer_id": "CU-003", "date": "2024-03-01", "credit_score": 670},
        ]
        self._credit_score_history_df = pd.DataFrame(credit_score_history_data)

        # Customer cashflow data
        customer_cashflow_data = [
            {"customer_id": "CU-001", "monthly_income_avg": 3500.00, "income_variability_pct": 10.0,
             "essential_expenses_avg": 1800.00},
            {"customer_id": "CU-002", "monthly_income_avg": 2500.00, "income_variability_pct": 15.0,
             "essential_expenses_avg": 1600.00},
            {"customer_id": "CU-003", "monthly_income_avg": 4200.00, "income_variability_pct": 8.0,
             "essential_expenses_avg": 2200.00},
        ]
        self._customer_cashflow_df = pd.DataFrame(customer_cashflow_data)

    def get_loans(self) -> pd.DataFrame:
        return self._loans_df.copy()

    def get_cards(self) -> pd.DataFrame:
        return self._cards_df.copy()

    def get_payments_history(self) -> pd.DataFrame:
        return self._payments_history_df.copy()

    def get_credit_score_history(self) -> pd.DataFrame:
        return self._credit_score_history_df.copy()

    def get_customer_cashflow(self) -> pd.DataFrame:
        return self._customer_cashflow_df.copy()

    def get_customer_data(self, customer_id: str) -> dict:
        """Get all data for a specific customer"""
        return {
            'loans': self._loans_df[self._loans_df['customer_id'] == customer_id].copy(),
            'cards': self._cards_df[self._cards_df['customer_id'] == customer_id].copy(),
            'payments_history': self._payments_history_df[self._payments_history_df['customer_id'] == customer_id].copy(),
            'credit_score_history': self._credit_score_history_df[self._credit_score_history_df['customer_id'] == customer_id].copy(),
            'customer_cashflow': self._customer_cashflow_df[self._customer_cashflow_df['customer_id'] == customer_id].copy()
        }

    def close(self):
        pass


def get_db() -> Generator[MockDatabase, None, None]:
    """Get database instance for dependency injection"""
    db = MockDatabase()
    try:
        yield db
    finally:
        db.close()
