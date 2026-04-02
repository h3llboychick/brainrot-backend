from fastapi import FastAPI
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from starlette import status

from src.domain.exceptions.base import BaseAppException


def setup_exception_handlers(app: FastAPI):
    @app.exception_handler(BaseAppException)
    async def base_app_exception_handler(request, exc: BaseAppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.message},
        )

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exceeded_handler(request, exc: RateLimitExceeded):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"message": "Rate limit exceeded. Please try again later."},
        )
