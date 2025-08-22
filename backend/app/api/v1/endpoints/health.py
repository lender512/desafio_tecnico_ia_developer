from fastapi import APIRouter
from datetime import datetime

from app.schemas import HealthResponse, MessageResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(status="healthy", timestamp=datetime.now())


@router.get("/", response_model=MessageResponse)
async def root():
    """Root endpoint"""
    return MessageResponse(message="Welcome to FastAPI Template", docs="/docs")
