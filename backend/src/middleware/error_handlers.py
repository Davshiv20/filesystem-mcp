from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from ..models import ErrorResponse


def setup_error_handlers(app: FastAPI):
    """Setup error handlers for the FastAPI application"""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request, exc):
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(error=exc.detail).dict()
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error="Internal server error",
                detail=str(exc)
            ).dict()
        ) 