"""
Base schemas for common response patterns
"""
from typing import Optional, Generic, TypeVar
from datetime import datetime
from pydantic import BaseModel, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration"""
    model_config = ConfigDict(
        from_attributes=True,
        arbitrary_types_allowed=True,
        str_strip_whitespace=True
    )


class HealthResponse(BaseSchema):
    """Health check response schema"""
    status: str
    timestamp: datetime


class MessageResponse(BaseSchema):
    """Generic message response schema"""
    message: str
    docs: Optional[str] = None


class ErrorResponse(BaseSchema):
    """Error response schema"""
    error: str
    detail: Optional[str] = None
    code: Optional[int] = None


class SuccessResponse(BaseSchema, Generic[T]):
    """Success response schema"""
    message: str
    data: Optional[T] = None
