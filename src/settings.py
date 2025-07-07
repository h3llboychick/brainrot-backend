from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    SESSION_MIDDLEWARE_SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file= ".env",
        env_file_encoding= "utf-8",
        extra="ignore"
    )

settings = AppSettings()