from pydantic_settings import BaseSettings, SettingsConfigDict


class YoutubeAuthSettings(BaseSettings):
    YOUTUBE_CLIENT_SECRET_FILE_PATH: str
    YOUTUBE_REDIRECT_URI: str
    YOUTUBE_SCOPES_LIST: list[str] = [
        "https://www.googleapis.com/auth/youtube.upload",
        "https://www.googleapis.com/auth/youtube.readonly",
    ]

    GOOGLE_CLIENT_ID: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


youtube_auth_settings = YoutubeAuthSettings()
