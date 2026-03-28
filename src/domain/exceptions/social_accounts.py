from src.domain.exceptions.base import BaseAppException


class UnsupportedSocialPlatformError(BaseAppException):
    """Raised when an unsupported or invalid platform is provided."""

    status_code = 400

    def __init__(
        self, platform: str | None = None, valid_platforms: list[str] | None = None
    ):
        if platform and valid_platforms:
            message = f"Unsupported platform: '{platform}'. Valid platforms: {', '.join(valid_platforms)}"
        elif platform:
            message = f"Unsupported platform: '{platform}'"
        else:
            message = "Invalid platform provided"
        super().__init__(message=message)


class ValidatorNotFoundError(BaseAppException):
    """Raised when no validator is registered for a platform."""

    status_code = 500

    def __init__(self, platform: str | None = None):
        message = f"No validator configured for platform: '{platform}'. This platform may not be fully implemented yet."
        super().__init__(message=message)


class NoYouTubeChannelFoundError(BaseAppException):
    """Raised when authenticated user has no YouTube channel."""

    status_code = 400

    def __init__(self):
        message = "No YouTube channel found for the authenticated user. Please create a YouTube channel first."
        super().__init__(message=message)
