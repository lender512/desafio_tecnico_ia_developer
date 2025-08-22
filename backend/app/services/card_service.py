"""
Card service for retrieving credit card information
"""
from typing import List, Optional
from fastapi import Depends

from ..db.database import MockDatabase, get_db
from ..schemas.card import Card


class CardService:
    """Service for credit card-related operations (read-only)"""

    def __init__(self, db: MockDatabase = Depends(get_db)):
        self.db = db

    def get_card_by_id(self, card_id: str) -> Optional[Card]:
        """Get a specific card by ID"""
        cards_df = self.db.get_cards()
        card_data = cards_df[cards_df['card_id'] == card_id]

        if card_data.empty:
            return None

        return Card(**card_data.iloc[0].to_dict())

    def get_cards_by_customer(self, customer_id: str) -> List[Card]:
        """Get all cards for a specific customer"""
        cards_df = self.db.get_cards()
        customer_cards = cards_df[cards_df['customer_id'] == customer_id]

        return [
            Card(**row.to_dict())
            for _, row in customer_cards.iterrows()
        ]

    def get_all_cards(self) -> List[Card]:
        """Get all cards in the system"""
        cards_df = self.db.get_cards()

        return [
            Card(**row.to_dict())
            for _, row in cards_df.iterrows()
        ]
