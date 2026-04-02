from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.video_job import VideoJob


class VideoJobRepository:
    def __init__(self, session: Session):
        self._session = session

    def get_by_id(self, job_id: str) -> VideoJob | None:
        return self._session.execute(
            select(VideoJob).where(VideoJob.id == job_id)
        ).scalar_one_or_none()

    def update_status(self, job_id: str, status: str) -> None:
        """Update the status of a video job."""
        video_job = self.get_by_id(job_id)
        if video_job:
            video_job.status = status
