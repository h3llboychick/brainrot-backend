from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class CryptoSettings(BaseSettings):
    KEK_KEY: str
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


@lru_cache
def get_settings() -> CryptoSettings:
    return CryptoSettings()
