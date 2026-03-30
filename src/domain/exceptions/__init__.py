from src.domain.exceptions.account_validation import (
    ExpiredSocialAccountCredentialsError,
    InvalidSocialAccountCredentialsError,
    NotFoundSocialAccountError,
)
from src.domain.exceptions.auth import (
    AccountStatusError,
    AuthenticationError,
    InvalidCredentialsError,
    InvalidVerificationCodeError,
    UserNotActiveError,
    UserNotVerifiedError,
    VerificationCodeError,
    VerificationCodeNotFoundError,
)
from src.domain.exceptions.base import BaseAppException
from src.domain.exceptions.db import (
    DBError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src.domain.exceptions.oauth import (
    InvalidOAuthStateError,
    OAuthAuthorizationError,
    OAuthCredentialsError,
    OAuthError,
    OAuthTokenExchangeError,
)
from src.domain.exceptions.social_accounts import (
    NoYouTubeChannelFoundError,
    UnsupportedSocialPlatformError,
    ValidatorNotFoundError,
)
from src.domain.exceptions.tokens import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenPayloadError,
    InvalidTokenTypeError,
    TokenAlreadyRevokedError,
    TokenError,
    TokenInactiveError,
    TokenNotFoundError,
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
