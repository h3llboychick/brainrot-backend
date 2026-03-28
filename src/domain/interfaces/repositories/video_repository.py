from src.domain.entities import VideoFormat, VideoJob

from abc import ABC, abstractmethod


class IVideoRepository(ABC):
    @abstractmethod
    async def get_video_format_by_id(self, format_id: int) -> VideoFormat | None:
        """
        Retrieve video format specifications.
        """
        pass

    @abstractmethod
    async def create_video_job(self, video_job: VideoJob) -> VideoJob:
        """
        Store a new video job in the database.
        """
        pass
