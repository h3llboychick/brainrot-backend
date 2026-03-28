from src.infrastructure.logging import setup_logging, get_logger
from src.infrastructure.redis import init_redis, close_redis
from src.infrastructure.db import init_db, close_db
from .settings import settings

from src.presentation.routers.auth.auth import router as auth_router
from src.presentation.routers.videos.videos import router as videos_router
from src.presentation.routers.accounts.accounts import router as accounts_router
from src.presentation.routers.users.users import router as users_router

from src.presentation.middlewares.error_handler import setup_exception_handlers

from contextlib import asynccontextmanager
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI
import uvicorn


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
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(videos_router)
    app.include_router(accounts_router)

    # Middlewares
    app.add_middleware(
        SessionMiddleware, secret_key=settings.SESSION_MIDDLEWARE_SECRET_KEY
    )
    setup_exception_handlers(app)

    uvicorn.run(app, host="127.0.0.1", port=8000)
