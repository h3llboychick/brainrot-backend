from src.domain.exceptions.base import BaseAppException


class TokenError(BaseAppException):
    """Base exception for token-related errors."""

    pass


class InvalidTokenError(TokenError):
    def __init__(self):
        super().__init__("Invalid token provided")


class ExpiredTokenError(TokenError):
    def __init__(self):
        super().__init__("Token has expired")


class InvalidTokenPayloadError(TokenError):
    def __init__(self):
        super().__init__("Invalid token payload")


class InvalidTokenTypeError(TokenError):
    def __init__(self):
        super().__init__("Invalid token type")


class TokenInactiveError(TokenError):
    def __init__(self):
        super().__init__("Token is inactive")


class TokenNotFoundError(TokenError):
    def __init__(self):
        super().__init__("Token not found")


class TokenAlreadyRevokedError(TokenError):
    def __init__(self):
        super().__init__("Token has been revoked")
