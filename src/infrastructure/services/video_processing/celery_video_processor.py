from src.domain.interfaces.services import IVideoProcessor
from src.domain.dtos.videos import VideoProcessingRequestDTO

from src.infrastructure.celery_app import app as celery_app

from celery import chain, signature


class CeleryVideoProcessor(IVideoProcessor):
    """
    Implementation of video processing using Celery for asynchronous task execution.

    Dispatches tasks by name via `send_task` / task signatures so that the API
    process never imports (or executes) any worker task code.
    """

    def schedule_generation(self, dto: VideoProcessingRequestDTO) -> None:
        """
        Schedule video generation using Celery task queue.

        If a platform is specified a task chain is built: generate → publish.
        Otherwise only the generation task is queued.
        """
        if dto.platform is None:
            celery_app.send_task(
                "generate_video",
                args=[dto.video_job_id, dto.format],
                queue="video.generate",
            )
        else:
            sig = chain(
                signature(
                    "generate_video",
                    args=[dto.video_job_id, dto.format],
                ).set(queue="video.generate"),
                signature(
                    "publish_video",
                    kwargs={
                        "user_id": dto.user_id,
                        "platform": dto.platform,
                        "metadata": dto.metadata,
                    },
                ).set(queue="video.publish"),
            )
            sig.apply_async()


# Singleton instance
video_processor = CeleryVideoProcessor()
