from src.domain.interfaces.services.social_account_validator import ISocialAccountValidator
from src.domain.exceptions.account_validation import InvalidSocialAccountCredentialsError, ExpiredSocialAccountCredentialsError
from src.domain.dtos.social_accounts.base import SocialAccountStatusDTO

from src.infrasturcture.logging.logger import get_logger
from .settings import youtube_validator_settings

from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from google.auth.exceptions import RefreshError


logger = get_logger("app.validators.youtube_validator")


class YouTubeAccountValidator(ISocialAccountValidator):
    async def validate_credentials(self, credentials: dict) -> SocialAccountStatusDTO:
        try:
            logger.debug("Building YouTube API client with credentials")

            # Adding Google API credentials
            info = {
                "token": credentials.get("token"),
                "refresh_token": credentials.get("refresh_token"),
                "token_uri": credentials.get("token_uri", "https://oauth2.googleapis.com/token"),
                "client_id": youtube_validator_settings.YOUTUBE_CLIENT_ID,
                "client_secret": youtube_validator_settings.YOUTUBE_CLIENT_SECRET,
                "scopes": credentials.get("scopes", ["https://www.googleapis.com/auth/youtube.upload"]),
            }

            # Build OAuth2 credentials
            creds = Credentials.from_authorized_user_info(
                info=info,
                scopes=["https://www.googleapis.com/auth/youtube.upload"]
            )
            
            creds.refresh(GoogleRequest())
        except RefreshError as e:
            logger.error(f"Failed to refresh YouTube credentials: {str(e)}")
            raise ExpiredSocialAccountCredentialsError(message="YouTube credentials have expired") from e
        except Exception as e:
            logger.error(f"Failed to validate YouTube credentials: {str(e)}")
            raise InvalidSocialAccountCredentialsError(message="YouTube credentials are invalid") from e


# Singleton instance
youtube_validator = YouTubeAccountValidator()
