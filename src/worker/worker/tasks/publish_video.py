from celery import shared_task
from celery.utils.log import get_logger

from ..clients.minio import get_minio_client
from ..db.database import sessionmanager
from ..db.repositories.social_accounts_repository import (
    SocialAccountsRepository,
)
from ..services.credentials_manager import get_credentials_manager
from ..services.platform_publishers.registry import PlatformPublisherRegistry
from ..services.video_storage_manager import get_video_storage_manager
from ..utils.encryption import encryption_manager

logger = get_logger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="video.publish",
    name="publish_video",
)
def publish_video(
    self,
    job_id: str,
    user_id: str,
    platform: str = "youtube",
    metadata: dict | None = None,
) -> dict:
    """
    Publish a video to a social media platform.

    Args:
        job_id: Video job identifier
        user_id: User identifier who owns the social account
        platform: Platform to publish to ('youtube', 'tiktok', 'instagram')
        metadata: Platform-specific metadata (title, description, etc.)
            If not provided, will use default test metadata.

    Returns:
        Dictionary with publish results (platform_id, published_url, status)

    Raises:
        ValueError: If platform is not supported or metadata is invalid
        RuntimeError: If upload fails
    """
    metadata = metadata or {}

    logger.info(f"Publishing video for job_id={job_id} to platform={platform}")

    # Check if platform is supported
    if not PlatformPublisherRegistry.is_supported(platform):
        available = PlatformPublisherRegistry.list_platforms()
        raise ValueError(
            f"Platform '{platform}' is not supported. "
            f"Available platforms: {', '.join(available)}"
        )

    # Get decrypted credentials
    with sessionmanager.session() as session:
        social_accounts_repository = SocialAccountsRepository(session)
        credentials_manager = get_credentials_manager(
            encryption_manager=encryption_manager,
            social_accounts_repository=social_accounts_repository,
        )
        credentials_dict = credentials_manager.get_decrypted_credentials(
            user_id, platform=platform
        )

    # Get platform-specific publisher
    publisher = PlatformPublisherRegistry.get_publisher(
        platform, credentials_dict
    )

    # Get video URL from storage
    video_storage_manager = get_video_storage_manager(get_minio_client())
    video_url = video_storage_manager.get_video_url(object_name=f"{job_id}.mp4")

    # Use default test metadata if none provided
    if not metadata:
        metadata = {
            "title": "Test Video Upload",
            "description": "This is a test video upload via automated system",
            "category": "22",  # People & Blogs
            "keywords": "test,upload,api",
            "privacyStatus": "private",
        }
        logger.info(f"Using default metadata for {platform}")

    # Publish to platform
    try:
        result = publisher.publish(video_url=str(video_url), metadata=metadata)

        logger.info(
            f"Successfully published to {platform}: "
            f"platform_id={result.get('platform_id')}, "
            f"url={result.get('published_url')}"
        )

        return result

    except Exception as e:
        logger.error(f"Failed to publish to {platform}: {e}", exc_info=True)
        raise
