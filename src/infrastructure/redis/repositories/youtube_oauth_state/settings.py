from pydantic_settings import BaseSettings


class YouTubeOAuthRepositorySettings(BaseSettings):
    STATE_TTL_SECONDS: int = 300  # 5 minutes


settings = YouTubeOAuthRepositorySettings()
