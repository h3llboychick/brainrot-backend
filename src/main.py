from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from slowapi.middleware import SlowAPIMiddleware
from starlette.middleware.sessions import SessionMiddleware

from src.infrastructure.db import db
from src.infrastructure.db.settings import get_settings as get_db_settings
from src.infrastructure.logging import get_logger, setup_logging
from src.infrastructure.rate_limiting import limiter
from src.infrastructure.redis import redis_client
from src.infrastructure.redis.settings import get_settings as get_redis_settings
from src.infrastructure.services.email.settings import (
    get_settings as get_email_settings,
)
from src.infrastructure.services.encryption.settings import (
    get_settings as get_crypto_settings,
)
from src.infrastructure.services.jwt.jwt_settings import (
    get_settings as get_jwt_settings,
)
from src.infrastructure.services.validators.settings import (
    get_youtube_validator_settings,
)
from src.presentation.middlewares.error_handler import setup_exception_handlers
from src.presentation.routers.accounts.accounts import router as accounts_router
from src.presentation.routers.auth.auth import init_oauth
from src.presentation.routers.auth.auth import router as auth_router
from src.presentation.routers.users.users import router as users_router
from src.presentation.routers.videos.videos import router as videos_router

from .settings import get_settings


def _validate_all_settings():
    """
    Eagerly load every settings class so that missing env vars
    cause a clear ValidationError at startup, not on the first request.
    """
    get_settings()
    get_db_settings()
    get_redis_settings()
    get_jwt_settings()
    get_crypto_settings()
    get_email_settings()
    get_youtube_validator_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    _validate_all_settings()
    app.state.oauth = init_oauth()
    redis_client.init()
    db.init()
    yield
    await redis_client.close()
    await db.close()


def run():
    setup_logging()
    app = FastAPI(lifespan=lifespan)

    logger = get_logger("app")
    logger.info("Starting application...")

    app_settings = get_settings()

    # Routers
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(videos_router, prefix="/api/v1")
    app.include_router(accounts_router, prefix="/api/v1")

    # Rate limiting
    app.state.limiter = limiter

    # Middlewares
    app.add_middleware(
        SessionMiddleware, secret_key=app_settings.SESSION_MIDDLEWARE_SECRET_KEY
    )
    app.add_middleware(SlowAPIMiddleware)
    setup_exception_handlers(app)

    uvicorn.run(app, host="127.0.0.1", port=8000)
