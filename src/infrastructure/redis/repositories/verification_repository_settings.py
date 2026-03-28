from pydantic_settings import BaseSettings


class VerificationRepositorySettings(BaseSettings):
    VERIFICATION_CODE_EXPIRATION_SECONDS: int = 900  # 15 minutes


settings = VerificationRepositorySettings()
