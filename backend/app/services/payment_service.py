"""
Payment service for retrieving payment history information
"""
from typing import List
import pandas as pd
from fastapi import Depends

from ..db.database import MockDatabase, get_db
from ..schemas.payment import Payment


class PaymentService:
    """Service for payment-related operations (read-only)"""

    def __init__(self, db: MockDatabase = Depends(get_db)):
        self.db = db

    def get_payments_by_customer(self, customer_id: str) -> List[Payment]:
        """Get all payments for a specific customer"""
        payments_df = self.db.get_payments_history()
        customer_payments = payments_df[payments_df['customer_id'] == customer_id]
        
        return [
            Payment(**row.to_dict()) 
            for _, row in customer_payments.iterrows()
        ]

    def get_payments_by_product(self, product_id: str) -> List[Payment]:
        """Get all payments for a specific product (loan or card)"""
        payments_df = self.db.get_payments_history()
        product_payments = payments_df[payments_df['product_id'] == product_id]
        
        return [
            Payment(**row.to_dict()) 
            for _, row in product_payments.iterrows()
        ]

    def get_all_payments(self) -> List[Payment]:
        """Get all payments in the system"""
        payments_df = self.db.get_payments_history()
        
        return [
            Payment(**row.to_dict()) 
            for _, row in payments_df.iterrows()
        ]
