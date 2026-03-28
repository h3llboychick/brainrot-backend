from abc import ABC, abstractmethod


class ISocialAccountValidator(ABC):
    """
    Interface for validating social media account credentials.

    Each platform (YouTube, TikTok, Instagram) implements this interface
    with their own API calls to verify credentials are still valid.
    """

    @abstractmethod
    async def validate_credentials(self, credentials: dict):
        """
        Raises:
            InvalidCredentialsError: If credentials are invalid or expired
            PlatformAPIError: If the platform API call fails
        """
        pass
