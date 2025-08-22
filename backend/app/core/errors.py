# errors.py
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse

from app.schemas.base import ErrorResponse

async def http_exc_handler(_: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="HTTPException",
                              detail=str(exc.detail),
                              code=exc.status_code).model_dump()
    )

def register_error_handlers(app):
    app.add_exception_handler(HTTPException, http_exc_handler)
