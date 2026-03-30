from io import BytesIO

import requests
from celery.utils.log import get_task_logger
from google.auth.transport.requests import Request as GoogleRequest
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseUpload

from ...domain.platform_publisher import PlatformPublisher
from ...services.platform_publishers.registry import PlatformPublisherRegistry
from ...settings import settings as worker_settings

logger = get_task_logger(__name__)


@PlatformPublisherRegistry.register
class YouTubePublisher(PlatformPublisher):
    platform_name = "youtube"

    def __init__(self, credentials: Credentials):
        """
        Initialize YouTube publisher.

        Args:
            youtube_service: Configured YouTubeService instance
        """
        self.youtube_client = build("youtube", "v3", credentials=credentials)

    @classmethod
    def from_credentials_dict(
        cls, credentials_dict: dict
    ) -> "YouTubePublisher":
        scopes = credentials_dict.get("scopes") or [
            "https://www.googleapis.com/auth/youtube.upload"
        ]
        if isinstance(scopes, str):
            scopes = [scopes]

        info = {
            "token": credentials_dict.get("token"),
            "refresh_token": credentials_dict.get("refresh_token"),
            "token_uri": credentials_dict.get("token_uri"),
            "client_id": credentials_dict.get("client_id")
            or worker_settings.GOOGLE_CLIENT_ID,
            "client_secret": credentials_dict.get("client_secret")
            or worker_settings.GOOGLE_CLIENT_SECRET,
            "scopes": scopes,
        }

        missing = [
            key
            for key in (
                "refresh_token",
                "token_uri",
                "client_id",
                "client_secret",
            )
            if not info.get(key)
        ]
        if missing:
            missing_str = ", ".join(missing)
            logger.error(
                "Stored YouTube credentials are missing required fields: %s."
                " Re-run the YouTube account linking flow or refresh stored credentials.",
                missing_str,
            )
            raise RuntimeError(
                "Stored YouTube credentials are missing required fields: "
                f"{missing_str}. Re-run the YouTube account linking flow."
            )

        credentials = Credentials.from_authorized_user_info(info, scopes=scopes)

        if not credentials.valid:
            if credentials.refresh_token:
                logger.info("Refreshing expired YouTube credentials")
                credentials.refresh(GoogleRequest())
            else:
                logger.error(
                    "YouTube credentials lack a refresh token; user must re-authorize account."
                )
                raise RuntimeError(
                    "YouTube credentials lack refresh token; user must re-authorize."
                )

        return cls(credentials)

    def validate_metadata(self, metadata: dict) -> None:
        """
        Validate YouTube-specific metadata.

        Required fields:
            - title: Video title
            - description: Video description
            - category: YouTube category ID (string number)

        Optional fields:
            - keywords: Comma-separated keywords or list
            - privacyStatus: 'public', 'private', or 'unlisted' (default: 'private')

        Args:
            metadata: Metadata to validate

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ["title", "description", "category"]
        missing = [field for field in required_fields if field not in metadata]

        if missing:
            raise ValueError(
                f"Missing required YouTube metadata fields: {', '.join(missing)}. "
                f"Required: {', '.join(required_fields)}"
            )

        # Validate privacy status if provided
        privacy = metadata.get("privacyStatus", "private")
        valid_privacy = ["public", "private", "unlisted"]
        if privacy not in valid_privacy:
            raise ValueError(
                f"Invalid privacyStatus: '{privacy}'. "
                f"Must be one of: {', '.join(valid_privacy)}"
            )

    def publish(self, video_url: str, metadata: dict) -> dict:
        self.validate_metadata(metadata)

        tags = metadata.get("keywords")
        tags = tags.split(",") if tags else None

        body = {
            "snippet": {
                "title": metadata["title"],
                "description": metadata["description"],
                "tags": tags,
                "categoryId": metadata["category"],
            },
            "status": {"privacyStatus": metadata["privacyStatus"]},
        }

        # Download video from URL into memory buffer
        buffer = BytesIO()
        response = requests.get(video_url, stream=True)  # nosec: B113

        for chunk in response.iter_content(chunk_size=8192):
            buffer.write(chunk)

        buffer.seek(0)

        # Upload to YouTube
        media = MediaIoBaseUpload(
            buffer,
            mimetype="video/mp4",
            chunksize=-1,  # Upload in single request
            resumable=True,
        )

        request = self.youtube_client.videos().insert(
            part="snippet,status", body=body, media_body=media
        )

        video_upload_response: dict | None = None
        try:
            while video_upload_response is None:
                status, video_upload_response = request.next_chunk()
                if status:
                    progress = int(status.progress() * 100)
                    logger.info(f"Upload progress: {progress}%")

            video_id = video_upload_response["id"]
            logger.info(f"Upload complete. Video ID: {video_id}")

            return {
                "platform_id": video_id,
                "published_url": f"https://youtube.com/shorts/{video_id}",
                "status": "published",
            }

        except HttpError as e:
            logger.error(f"HTTP error during YouTube upload: {e}")
            raise
        finally:
            buffer.close()
