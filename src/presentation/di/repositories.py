from src.infrasturcture.db.database import get_db_session
from src.infrasturcture.db.repositories.token_repository import TokenRepository
from src.infrasturcture.db.repositories.user_repository import UserRepository
from src.infrasturcture.db.repositories.video_repository import VideoRepository
from src.infrasturcture.db.repositories.social_accounts_repository import SocialAccountsRepository

from src.infrasturcture.redis.redis import redis_connection_manager
from src.infrasturcture.redis.repositories.verification_code_repository import VerificationCodeRepository
from src.infrasturcture.redis.repositories.youtube_oauth_state.youtube_oauth_state_repository import YouTubeOAuthStateRepository

from src.domain.interfaces.services.token_hasher import ITokenHasher

from src.presentation.di.services import get_token_hasher

from fastapi import Depends
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from typing import Annotated


def get_token_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)],
    token_hasher: Annotated[ITokenHasher, Depends(get_token_hasher)]
) -> TokenRepository:
    return TokenRepository(db_session=db_session, token_hasher=token_hasher)

def get_user_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> UserRepository:
    return UserRepository(db_session=db_session)

def get_video_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> UserRepository:
    return VideoRepository(db_session=db_session)

def get_verification_code_repository(
    redis_session: Annotated[Redis, Depends(redis_connection_manager.get_client)]
) -> VerificationCodeRepository:
    return VerificationCodeRepository(redis_session)

def get_youtube_oauth_state_repository(
    redis_session: Annotated[Redis, Depends(redis_connection_manager.get_client)]
):
    return YouTubeOAuthStateRepository(redis_session)
    
def get_social_accounts_repository(
    db_session: Annotated[AsyncSession, Depends(get_db_session)]
) -> SocialAccountsRepository:
    return SocialAccountsRepository(db_session=db_session)
