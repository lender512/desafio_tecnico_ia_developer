"""
Cashflow service for retrieving customer cashflow information
"""
from typing import List, Optional
from fastapi import Depends

from ..db.database import MockDatabase, get_db
from ..schemas.cashflow import CustomerCashflow


class CashflowService:
    """Service for cashflow-related operations (read-only)"""

    def __init__(self, db: MockDatabase = Depends(get_db)):
        self.db = db

    def get_customer_cashflow(self, customer_id: str) -> Optional[CustomerCashflow]:
        """Get cashflow information for a specific customer"""
        cashflow_df = self.db.get_customer_cashflow()
        customer_data = cashflow_df[cashflow_df['customer_id'] == customer_id]
        
        if customer_data.empty:
            return None
        
        return CustomerCashflow(**customer_data.iloc[0].to_dict())

    def get_all_cashflows(self) -> List[CustomerCashflow]:
        """Get all customer cashflow records"""
        cashflow_df = self.db.get_customer_cashflow()
        
        return [
            CustomerCashflow(**row.to_dict()) 
            for _, row in cashflow_df.iterrows()
        ]
