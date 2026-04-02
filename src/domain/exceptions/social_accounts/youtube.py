from src.domain.exceptions.social_accounts.base import SocialAccountError


class YouTubeChannelNotFoundError(SocialAccountError):
    """Raised when an authenticated user has no YouTube channel."""

    def __init__(self):
        super().__init__(
            "No YouTube channel found for the authenticated user. "
            "Please create a YouTube channel first."
        )
