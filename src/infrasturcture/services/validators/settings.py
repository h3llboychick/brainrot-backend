from pydantic_settings import BaseSettings, SettingsConfigDict

class YouTubeValidatorSettings(BaseSettings):
    YOUTUBE_CLIENT_ID: str
    YOUTUBE_CLIENT_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

youtube_validator_settings = YouTubeValidatorSettings()