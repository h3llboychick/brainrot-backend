from src.domain.entities.video_format import VideoFormat
from src.domain.entities.video_job import VideoJob

from abc import ABC, abstractmethod


class IVideoRepository(ABC):
    @abstractmethod
    async def get_video_format_by_id(self, format_id: int) -> VideoFormat:
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