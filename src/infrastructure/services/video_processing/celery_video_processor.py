from src.domain.interfaces.services.video_processor import IVideoProcessor
from src.domain.dtos.videos.processing import VideoProcessingRequestDTO

from src.infrastructure.worker.worker.tasks.generate_video import generate_video
from src.infrastructure.worker.worker.tasks.publish_video import publish_video

from celery import chain


class CeleryVideoProcessor(IVideoProcessor):
    """
    Implementation of video processing using Celery for asynchronous task execution.
    
    Handles queueing video generation tasks and orchestrating multi-step workflows
    (e.g., generate video → publish to platform).
    """
    
    def schedule_generation(self, dto: VideoProcessingRequestDTO) -> None:
        """
        Schedule video generation using Celery task queue.
        
        If platform is specified, creates a task chain: generate → publish.
        Otherwise, only schedules the generation task.
        """
        if dto.platform is None:
            # Simple generation only
            generate_video(
                dto.video_job_id, 
                dto.format
            ).delay()
        else:
            # Chain generation with publishing
            sig = chain(
                generate_video.s(
                    dto.video_job_id, 
                    dto.format
                ),
                publish_video.s(
                    dto.user_id,
                    dto.platform,
                    dto.metadata,
                ),
            )
            sig.apply_async()


# Singleton instance
video_processor = CeleryVideoProcessor()
