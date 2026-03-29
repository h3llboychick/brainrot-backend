from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.infrastructure.db import close_db, init_db
from src.infrastructure.logging import get_logger, setup_logging
from src.infrastructure.rate_limiting import limiter
from src.infrastructure.redis import close_redis, init_redis
from src.presentation.middlewares.error_handler import setup_exception_handlers
from src.presentation.routers.accounts.accounts import router as accounts_router
from src.presentation.routers.auth.auth import router as auth_router
from src.presentation.routers.users.users import router as users_router
from src.presentation.routers.videos.videos import router as videos_router

from .settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_redis()
    init_db()
    yield
    await close_redis()
    await close_db()


app = FastAPI(lifespan=lifespan)


def run():
    setup_logging()

    logger = get_logger("app")
    logger.info("Starting application...")

    # Routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(videos_router, prefix="/api/v1")
    app.include_router(accounts_router, prefix="/api/v1")

    # Rate limiting
    app.state.limiter = limiter

    # Middlewares
    app.add_middleware(
        SessionMiddleware, secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY
    )
    app.add_middleware(SlowAPIMiddleware)
    setup_exception_handlers(app)

    uvicorn.run(app, host="127.0.0.1", port=8000)
