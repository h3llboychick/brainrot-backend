from google.auth.exceptions import RefreshError
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials

from src.domain.dtos.social_accounts import SocialAccountStatusDTO
from src.domain.exceptions import (
    ExpiredSocialAccountCredentialsError,
    InvalidSocialAccountCredentialsError,
)
from src.domain.interfaces.services import ISocialAccountValidator
from src.infrastructure.logging import get_logger

from .settings import get_youtube_validator_settings

logger = get_logger("app.validators.youtube_validator")


class YouTubeAccountValidator(ISocialAccountValidator):
    async def validate_credentials(
        self, credentials: dict
    ) -> SocialAccountStatusDTO:
        try:
            logger.debug("Building YouTube API client with credentials")

            # Adding Google API credentials
            settings = get_youtube_validator_settings()
            info = {
                "token": credentials.get("token"),
                "refresh_token": credentials.get("refresh_token"),
                "token_uri": credentials.get(
                    "token_uri", "https://oauth2.googleapis.com/token"
                ),
                "client_id": settings.YOUTUBE_CLIENT_ID,
                "client_secret": settings.YOUTUBE_CLIENT_SECRET,
                "scopes": credentials.get(
                    "scopes", ["https://www.googleapis.com/auth/youtube.upload"]
                ),
            }

            # Build OAuth2 credentials
            creds = Credentials.from_authorized_user_info(
                info=info,
                scopes=["https://www.googleapis.com/auth/youtube.upload"],
            )

            creds.refresh(GoogleRequest())

            return SocialAccountStatusDTO(
                is_connected=True,
                expires_at=creds.expiry.isoformat() if creds.expiry else None,
            )
        except RefreshError as e:
            logger.error(f"Failed to refresh YouTube credentials: {str(e)}")
            raise ExpiredSocialAccountCredentialsError(
                message="YouTube credentials have expired"
            ) from e
        except Exception as e:
            logger.error(f"Failed to validate YouTube credentials: {str(e)}")
            raise InvalidSocialAccountCredentialsError(
                message="YouTube credentials are invalid"
            ) from e


# Singleton instance
youtube_validator = YouTubeAccountValidator()
