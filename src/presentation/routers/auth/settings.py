from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleAuthSettings(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_CLIENT_SECRET: str
    SECRET_KEY: str
    GOOGLE_REDIRECT_URL: str
    GOOGLE_FRONTEND_URL: str
    

    model_config = SettingsConfigDict(
        env_file= ".env",
        env_file_encoding= "utf-8",
        extra="ignore"
    )

google_auth_settings = GoogleAuthSettings()