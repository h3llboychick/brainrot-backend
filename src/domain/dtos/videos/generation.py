from pydantic import BaseModel


class VideoGenerationRequestDTO(BaseModel):
    user_id: str
    format_id: int
    prompt: str
    platform: str | None = None
    
class VideoGenerationResponseDTO(BaseModel):
    video_job_id: str

