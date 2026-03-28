from src.domain.interfaces.repositories.social_accounts_repository import (
    ISocialAccountsRepository,
)
from src.domain.interfaces.repositories.token_respository import ITokenRepository
from src.domain.interfaces.repositories.user_repository import IUserRepository
from src.domain.interfaces.repositories.verification_code_repository import (
    IVerificationCodeRepository,
)
from src.domain.interfaces.repositories.video_repository import IVideoRepository

__all__ = [
    "ISocialAccountsRepository",
    "ITokenRepository",
    "IUserRepository",
    "IVerificationCodeRepository",
    "IVideoRepository",
]
