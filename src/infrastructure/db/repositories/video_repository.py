from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import VideoFormat, VideoJob
from src.domain.interfaces.repositories import IVideoRepository
from src.infrastructure.db.models import VideoFormat as VideoFormatModel
from src.infrastructure.db.models import VideoJob as VideoJobModel


class VideoRepository(IVideoRepository):
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def get_video_format_by_id(
        self, format_id: int
    ) -> VideoFormat | None:
        query = select(VideoFormatModel).where(VideoFormatModel.id == format_id)
        result = (await self._session.execute(query)).scalar_one_or_none()
        return (
            VideoFormat.model_validate(result, from_attributes=True)
            if result
            else None
        )

    async def get_all_video_formats(self) -> list[VideoFormat]:
        query = select(VideoFormatModel)
        result = await self._session.execute(query)
        rows = result.scalars().all()
        return [
            VideoFormat.model_validate(row, from_attributes=True)
            for row in rows
        ]

    async def create_video_job(self, video_job: VideoJob) -> VideoJob:
        video_job_model = VideoJobModel(
            creator_id=video_job.creator_id,
            format_id=video_job.format_id,
            status=video_job.status,
        )
        self._session.add(video_job_model)
        await self._session.commit()
        await self._session.refresh(video_job_model)
        return VideoJob.model_validate(video_job_model, from_attributes=True)
