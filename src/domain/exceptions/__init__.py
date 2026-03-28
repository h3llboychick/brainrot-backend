from src.domain.exceptions.base import BaseAppException
from src.domain.exceptions.auth import (
    AuthenticationError,
    InvalidCredentialsError,
    AccountStatusError,
    UserNotVerifiedError,
    UserNotActiveError,
    VerificationCodeError,
    VerificationCodeNotFoundError,
    InvalidVerificationCodeError,
)
from src.domain.exceptions.db import (
    DBError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.domain.exceptions.oauth import (
    OAuthError,
    InvalidOAuthStateError,
    OAuthCredentialsError,
    OAuthTokenExchangeError,
    OAuthAuthorizationError,
)
from src.domain.exceptions.tokens import (
    TokenError,
    InvalidTokenError,
    ExpiredTokenError,
    InvalidTokenPayloadError,
    InvalidTokenTypeError,
    TokenInactiveError,
    TokenNotFoundError,
    TokenAlreadyRevokedError,
)
from src.domain.exceptions.social_accounts import (
    UnsupportedSocialPlatformError,
    ValidatorNotFoundError,
    NoYouTubeChannelFoundError,
)
from src.domain.exceptions.account_validation import (
    NotFoundSocialAccountError,
    InvalidSocialAccountCredentialsError,
    ExpiredSocialAccountCredentialsError,
)

__all__ = [
    "BaseAppException",
    "AuthenticationError",
    "InvalidCredentialsError",
    "AccountStatusError",
    "UserNotVerifiedError",
    "UserNotActiveError",
    "VerificationCodeError",
    "VerificationCodeNotFoundError",
    "InvalidVerificationCodeError",
    "DBError",
    "UserAlreadyExistsError",
    "UserNotFoundError",
    "OAuthError",
    "InvalidOAuthStateError",
    "OAuthCredentialsError",
    "OAuthTokenExchangeError",
    "OAuthAuthorizationError",
    "TokenError",
    "InvalidTokenError",
    "ExpiredTokenError",
    "InvalidTokenPayloadError",
    "InvalidTokenTypeError",
    "TokenInactiveError",
    "TokenNotFoundError",
    "TokenAlreadyRevokedError",
    "UnsupportedSocialPlatformError",
    "ValidatorNotFoundError",
    "NoYouTubeChannelFoundError",
    "NotFoundSocialAccountError",
    "InvalidSocialAccountCredentialsError",
    "ExpiredSocialAccountCredentialsError",
]
