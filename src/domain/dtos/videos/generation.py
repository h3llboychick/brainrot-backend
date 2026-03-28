from pydantic import BaseModel
from src.domain.enums import SocialPlatform


class VideoGenerationRequestDTO(BaseModel):
    user_id: str
    format_id: int
    prompt: str
    platform: SocialPlatform | None = None


class VideoGenerationResponseDTO(BaseModel):
    video_job_id: str
