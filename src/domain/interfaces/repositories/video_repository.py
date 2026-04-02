from abc import ABC, abstractmethod

from src.domain.entities import VideoFormat, VideoJob


class IVideoRepository(ABC):
    @abstractmethod
    async def get_video_format_by_id(
        self, format_id: int
    ) -> VideoFormat | None:
        """
        Retrieve video format specifications.
        """
        pass

    @abstractmethod
    async def get_all_video_formats(self) -> list[VideoFormat]:
        """
        Retrieve all available video formats.
        """
        pass

    @abstractmethod
    async def create_video_job(self, video_job: VideoJob) -> VideoJob:
        """
        Store a new video job in the database.
        """
        pass
