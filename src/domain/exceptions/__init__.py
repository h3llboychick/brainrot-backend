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
from src.domain.exceptions.oauth import (
    InvalidOAuthStateError,
    OAuthAuthorizationError,
    OAuthCredentialsError,
    OAuthError,
    OAuthTokenExchangeError,
)
from src.domain.exceptions.payments import (
    DuplicatePaymentError,
    InvalidPriceError,
    InvalidTokenCountError,
    PaymentError,
)
from src.domain.exceptions.social_accounts import (
    ExpiredSocialAccountCredentialsError,
    InvalidSocialAccountCredentialsError,
    PlatformValidatorNotFoundError,
    SocialAccountCredentialsError,
    SocialAccountError,
    SocialAccountNotFoundError,
    UnsupportedPlatformError,
    YouTubeChannelNotFoundError,
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
from src.domain.exceptions.users import (
    InsufficientBalanceError,
    UserAlreadyExistsError,
    UserError,
    UserNotFoundError,
)
from src.domain.exceptions.videos import (
    VideoError,
    VideoFormatNotFoundError,
)

__all__ = [
    "BaseAppException",
    # Auth
    "AuthenticationError",
    "InvalidCredentialsError",
    "AccountStatusError",
    "UserNotVerifiedError",
    "UserNotActiveError",
    "VerificationCodeError",
    "VerificationCodeNotFoundError",
    "InvalidVerificationCodeError",
    # Tokens
    "TokenError",
    "InvalidTokenError",
    "ExpiredTokenError",
    "InvalidTokenPayloadError",
    "InvalidTokenTypeError",
    "TokenInactiveError",
    "TokenNotFoundError",
    "TokenAlreadyRevokedError",
    # OAuth
    "OAuthError",
    "InvalidOAuthStateError",
    "OAuthCredentialsError",
    "OAuthTokenExchangeError",
    "OAuthAuthorizationError",
    # Users
    "UserError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "InsufficientBalanceError",
    # Payments
    "PaymentError",
    "InvalidPriceError",
    "InvalidTokenCountError",
    "DuplicatePaymentError",
    # Videos
    "VideoError",
    "VideoFormatNotFoundError",
    # Social Accounts
    "SocialAccountError",
    "SocialAccountNotFoundError",
    "SocialAccountCredentialsError",
    "InvalidSocialAccountCredentialsError",
    "ExpiredSocialAccountCredentialsError",
    "UnsupportedPlatformError",
    "PlatformValidatorNotFoundError",
    "YouTubeChannelNotFoundError",
]
