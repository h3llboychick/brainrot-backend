from src.domain.entities import VideoFormat
from src.domain.interfaces.repositories import IVideoRepository
from src.infrastructure.logging import get_logger

logger = get_logger("app.videos.list_video_formats")


class ListVideoFormatsUseCase:
    def __init__(self, video_repository: IVideoRepository):
        self.video_repository = video_repository

    async def execute(self) -> list[VideoFormat]:
        logger.info("Listing all available video formats")
        return await self.video_repository.get_all_video_formats()
