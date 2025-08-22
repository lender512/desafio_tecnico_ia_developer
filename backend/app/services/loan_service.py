"""
Loan service for retrieving loan information
"""
from typing import List, Optional
from decimal import Decimal
import pandas as pd
from fastapi import Depends

from ..db.database import MockDatabase, get_db
from ..schemas.loan import Loan


class LoanService:
    """Service for loan-related operations (read-only)"""

    def __init__(self, db: MockDatabase = Depends(get_db)):
        self.db = db

    def get_loan_by_id(self, loan_id: str) -> Optional[Loan]:
        """Get a specific loan by ID"""
        loans_df = self.db.get_loans()
        loan_data = loans_df[loans_df['loan_id'] == loan_id]
        
        if loan_data.empty:
            return None
        
        return Loan(**loan_data.iloc[0].to_dict())

    def get_loans_by_customer(self, customer_id: str) -> List[Loan]:
        """Get all loans for a specific customer"""
        loans_df = self.db.get_loans()
        customer_loans = loans_df[loans_df['customer_id'] == customer_id]
        
        return [
            Loan(**row.to_dict()) 
            for _, row in customer_loans.iterrows()
        ]

    def get_all_loans(self) -> List[Loan]:
        """Get all loans in the system"""
        loans_df = self.db.get_loans()
        
        return [
            Loan(**row.to_dict()) 
            for _, row in loans_df.iterrows()
        ]
