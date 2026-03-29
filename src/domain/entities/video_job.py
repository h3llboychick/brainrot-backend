from pydantic import BaseModel
from datetime import datetime, timezone

from src.domain.enums import VideoJobStatus


class VideoJob(BaseModel):
    id: str | None = None
    creator_id: str
    format_id: int
    status: VideoJobStatus = VideoJobStatus.queued
    video_url: str | None = None
    publish_automatically: bool = False
    scheduled_at: datetime | None = None
    created_at: datetime = datetime.now(tz=timezone.utc)
    published_at: datetime | None = None
    social_accounts_ids: list[str] = []

    def can_be_cancelled(self) -> bool:
        return self.status in ["queued", "processing", "scheduled"]

    def can_change_format(self) -> bool:
        return self.status in ["queued", "scheduled"]

    def can_be_deleted(self) -> bool:
        return self.status in ["done", "published"]
