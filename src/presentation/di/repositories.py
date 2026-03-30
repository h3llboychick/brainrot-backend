from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.interfaces.services import ITokenHasher
from src.infrastructure.db import db
from src.infrastructure.db.repositories import (
    SocialAccountsRepository,
    TokenRepository,
    UserRepository,
    VideoRepository,
)
from src.infrastructure.redis import redis_client
from src.infrastructure.redis.repositories import (
    VerificationCodeRepository,
    YouTubeOAuthStateRepository,
)
from src.presentation.di.services import get_token_hasher


def get_token_repository(
    db_session: Annotated[AsyncSession, Depends(db.get_session)],
    token_hasher: Annotated[ITokenHasher, Depends(get_token_hasher)],
) -> TokenRepository:
    return TokenRepository(db_session=db_session, token_hasher=token_hasher)


def get_user_repository(
    db_session: Annotated[AsyncSession, Depends(db.get_session)],
) -> UserRepository:
    return UserRepository(db_session=db_session)


def get_video_repository(
    db_session: Annotated[AsyncSession, Depends(db.get_session)],
) -> VideoRepository:
    return VideoRepository(db_session=db_session)


def get_verification_code_repository(
    redis_session: Annotated[Redis, Depends(redis_client.get_client)],
) -> VerificationCodeRepository:
    return VerificationCodeRepository(redis_session)


def get_youtube_oauth_state_repository(
    redis_session: Annotated[Redis, Depends(redis_client.get_client)],
):
    return YouTubeOAuthStateRepository(redis_session)


def get_social_accounts_repository(
    db_session: Annotated[AsyncSession, Depends(db.get_session)],
) -> SocialAccountsRepository:
    return SocialAccountsRepository(db_session=db_session)
