from abc import ABC, abstractmethod
from typing import Dict, Any


class PlatformPublisher(ABC):
    """
    Abstract base class for publishing videos to social media platforms.
    
    Each platform (YouTube, TikTok, Instagram, etc.) should implement this interface.
    """
    
    @property
    @abstractmethod
    def platform_name(self) -> str:
        """
        Returns the platform identifier (e.g., 'youtube', 'tiktok', 'instagram').
        
        Must match the platform name in SocialPlatform enum.
        """
        pass
    
    @abstractmethod
    def publish(
        self,
        video_url: str,
        metadata: dict
    ) -> dict:
        """
        Publish a video to the platform.
        
        Args:
            video_url: URL or path to the video file to upload
            metadata: Platform-specific metadata (title, description, tags, etc.)
                Each platform may require different fields.
        """
        pass
    
    @abstractmethod
    def validate_metadata(self, metadata: dict) -> None:
        """
        Validate that metadata contains all required fields for this platform.
        
        Args:
            metadata: Platform-specific metadata to validate
        """
        pass
