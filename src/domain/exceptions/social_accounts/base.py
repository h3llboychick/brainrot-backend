from src.domain.exceptions.base import BaseAppException


class SocialAccountError(BaseAppException):
    """Base exception for social account-related errors."""

    status_code = 400

    def __init__(self, message: str = "Social account error"):
        super().__init__(message)


class SocialAccountNotFoundError(SocialAccountError):
    """Raised when a social account is not found."""

    status_code = 404

    def __init__(self, message: str = "Social account not found"):
        super().__init__(message)


class SocialAccountCredentialsError(SocialAccountError):
    """Base exception for social account credential issues."""

    def __init__(self, message: str = "Social account credentials error"):
        super().__init__(message)


class InvalidSocialAccountCredentialsError(SocialAccountCredentialsError):
    """Raised when social account credentials are invalid."""

    def __init__(self, message: str = "Social account credentials are invalid"):
        super().__init__(message)


class ExpiredSocialAccountCredentialsError(SocialAccountCredentialsError):
    """Raised when social account credentials have expired."""

    def __init__(
        self, message: str = "Social account credentials have expired"
    ):
        super().__init__(message)


class UnsupportedPlatformError(SocialAccountError):
    """Raised when an unsupported or invalid platform is provided."""

    def __init__(
        self,
        platform: str | None = None,
        valid_platforms: list[str] | None = None,
    ):
        if platform and valid_platforms:
            message = f"Unsupported platform: '{platform}'. Valid platforms: {', '.join(valid_platforms)}"
        elif platform:
            message = f"Unsupported platform: '{platform}'"
        else:
            message = "Invalid platform provided"
        super().__init__(message=message)


class PlatformValidatorNotFoundError(SocialAccountError):
    """Raised when no validator is registered for a platform."""

    status_code = 500

    def __init__(self, platform: str | None = None):
        message = f"No validator configured for platform: '{platform}'. This platform may not be fully implemented yet."
        super().__init__(message=message)
