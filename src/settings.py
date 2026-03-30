from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    SESSION_MIDDLEWARE_SECRET_KEY: str
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"
    DEBUG: bool = False
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
