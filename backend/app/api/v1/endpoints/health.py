from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}


@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Welcome to FastAPI Template", "docs": "/docs"}
