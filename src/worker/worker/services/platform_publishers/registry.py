from typing import Dict, Type

from celery.utils.log import get_task_logger

from ...domain.platform_publisher import PlatformPublisher

logger = get_task_logger(__name__)


class PlatformPublisherRegistry:
    """
    Central registry for platform publisher implementations.

    Publishers register themselves using the @PlatformPublisherRegistry.register decorator.
    """

    _publishers: dict[str, Type[PlatformPublisher]] = {}

    @classmethod
    def register(
        cls, publisher_class: Type[PlatformPublisher]
    ) -> Type[PlatformPublisher]:
        """
        Decorator to register a platform publisher.

        Usage:
            @PlatformPublisherRegistry.register
            class YouTubePublisher(PlatformPublisher):
                ...

        Args:
            publisher_class: The publisher class to register

        Returns:
            The same class (allows use as decorator)
        """
        platform_name = publisher_class.platform_name

        if platform_name in cls._publishers:
            logger.warning(
                f"Platform publisher '{platform_name}' already registered, overwriting"
            )

        cls._publishers[platform_name] = publisher_class
        logger.info(f"Registered platform publisher: '{platform_name}'")

        return publisher_class

    @classmethod
    def get_publisher(
        cls, platform: str, credentials_dict: Dict
    ) -> PlatformPublisher:
        """
        Get a publisher instance for the specified platform.

        Args:
            platform: Platform identifier (e.g., 'youtube', 'tiktok')
            credentials_dict: Decrypted credentials for the platform

        Returns:
            Publisher instance configured with credentials

        Raises:
            ValueError: If platform is not supported
        """
        if platform not in cls._publishers:
            available = ", ".join(cls._publishers.keys())
            raise ValueError(
                f"Unsupported platform: '{platform}'. "
                f"Available platforms: {available or 'none'}"
            )

        publisher_class = cls._publishers[platform]
        return publisher_class.from_credentials_dict(credentials_dict)

    @classmethod
    def list_platforms(cls) -> list[str]:
        """Get list of all registered platform names."""
        return list(cls._publishers.keys())

    @classmethod
    def is_supported(cls, platform: str) -> bool:
        """Check if a platform is supported."""
        return platform in cls._publishers
