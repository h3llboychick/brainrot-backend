from pydantic_settings import BaseSettings

class BaseSettings(BaseSettings):
    VERIFICATION_CODE_EXPIRATION_SECONDS: int = 900  # 15 minutes

settings = BaseSettings()