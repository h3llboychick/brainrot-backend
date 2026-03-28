from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    SESSION_MIDDLEWARE_SECRET_KEY: str
    CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


settings = AppSettings()
