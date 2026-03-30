from abc import ABC, abstractmethod

from src.domain.dtos.videos import VideoProcessingRequestDTO


class IVideoProcessor(ABC):
    """
    Domain service for scheduling video generation processing.

    This service schedules video generation work for background processing
    but does NOT create the video job entity - that's the use case's responsibility.
    It orchestrates the actual video generation workflow (generate, publish).
    """

    @abstractmethod
    def schedule_generation(self, dto: VideoProcessingRequestDTO) -> None:
        """
        Schedule a video for background generation and optional publishing.

        Args:
            dto: Contains video job details and processing instructions
        """
        pass
