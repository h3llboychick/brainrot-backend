from functools import lru_cache

from pydantic_settings import BaseSettings


class YouTubeOAuthRepositorySettings(BaseSettings):
    STATE_TTL_SECONDS: int = 300  # 5 minutes


@lru_cache
def get_settings() -> YouTubeOAuthRepositorySettings:
    return YouTubeOAuthRepositorySettings()
