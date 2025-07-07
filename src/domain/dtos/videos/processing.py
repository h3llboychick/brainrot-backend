from pydantic import BaseModel

class VideoProcessingRequestDTO(BaseModel):
    video_job_id: str
    format: str
    user_id: str
    platform: str | None = None
    metadata: dict | None = None