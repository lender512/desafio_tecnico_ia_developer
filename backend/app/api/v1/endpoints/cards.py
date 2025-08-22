from typing import List
from app.schemas.base import SuccessResponse
from fastapi import APIRouter, Depends, HTTPException, status

from app.services.card_service import CardService
from app.schemas.card import Card

router = APIRouter()


@router.get("/cards", response_model=SuccessResponse[List[Card]])
async def get_all_cards(
    card_service: CardService = Depends()
):
    """Get all cards in the system"""
    # return card_service.get_all_cards()
    return SuccessResponse(message="All cards retrieved successfully", data=card_service.get_all_cards())


@router.get("/cards/{card_id}", response_model=SuccessResponse[Card])
async def get_card_by_id(
    card_id: str,
    card_service: CardService = Depends()
):
    """Get a specific card by ID"""
    card = card_service.get_card_by_id(card_id)
    if not card:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Card {card_id} not found"
        )
    return SuccessResponse(message="Card retrieved successfully",data=card)


@router.get("/customers/{customer_id}/cards", response_model=SuccessResponse[List[Card]])
async def get_cards_by_customer(
    customer_id: str,
    card_service: CardService = Depends()
):
    """Get all cards for a specific customer"""
    # return card_service.get_cards_by_customer(customer_id)
    return SuccessResponse(message="All cards retrieved successfully", data=card_service.get_cards_by_customer(customer_id))
