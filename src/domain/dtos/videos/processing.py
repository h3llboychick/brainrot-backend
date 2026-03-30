from pydantic import BaseModel

from src.domain.enums import SocialPlatform


class VideoProcessingRequestDTO(BaseModel):
    video_job_id: str
    format: str
    user_id: str
    platform: SocialPlatform | None = None
    metadata: dict | None = None
