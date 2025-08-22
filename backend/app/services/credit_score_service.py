"""
Credit score service for retrieving credit score information
"""
from typing import List, Optional
from fastapi import Depends

from ..db.database import MockDatabase, get_db
from ..schemas.credit_score import CreditScore


class CreditScoreService:
    """Service for credit score-related operations (read-only)"""

    def __init__(self, db: MockDatabase = Depends(get_db)):
        self.db = db

    def get_credit_scores_by_customer(self, customer_id: str) -> List[CreditScore]:
        """Get all credit scores for a specific customer"""
        credit_df = self.db.get_credit_score_history()
        customer_scores = credit_df[credit_df['customer_id'] == customer_id]
        
        return [
            CreditScore(**row.to_dict()) 
            for _, row in customer_scores.iterrows()
        ]

    def get_current_credit_score(self, customer_id: str) -> Optional[CreditScore]:
        """Get the most recent credit score for a customer"""
        credit_df = self.db.get_credit_score_history()
        customer_scores = credit_df[credit_df['customer_id'] == customer_id]
        
        if customer_scores.empty:
            return None
        
        # Get most recent score
        most_recent = customer_scores.sort_values('date', ascending=False).iloc[0]
        return CreditScore(**most_recent.to_dict())

    def get_all_credit_scores(self) -> List[CreditScore]:
        """Get all credit scores in the system"""
        credit_df = self.db.get_credit_score_history()
        
        return [
            CreditScore(**row.to_dict()) 
            for _, row in credit_df.iterrows()
        ]
