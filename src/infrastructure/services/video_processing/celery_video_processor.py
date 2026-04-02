from functools import lru_cache

from celery import chain, signature

from src.domain.dtos.videos import VideoProcessingRequestDTO
from src.domain.interfaces.services import IVideoProcessor
from src.infrastructure.celery_app import get_celery_app


class CeleryVideoProcessor(IVideoProcessor):
    """
    Implementation of video processing using Celery for asynchronous task execution.

    Dispatches tasks by name via `send_task` / task signatures so that the API
    process never imports (or executes) any worker task code.

    Builds a saga chain:
      generate_video -> confirm_charge -> (optional) publish_video
    with a compensating task (compensate_failed_job) attached via link_error.
    """

    def schedule_generation(self, dto: VideoProcessingRequestDTO) -> None:
        """
        Schedule video generation using Celery task queue.

        The chain always includes: generate -> confirm_charge.
        If a platform is specified, publish_video is appended.
        On failure of generate_video, compensate_failed_job fires to
        release the balance reservation.
        """

        get_celery_app()  # noqa: F841 — ensures app is initialized

        billing_kwargs = {
            "job_id": dto.video_job_id,
            "user_id": dto.user_id,
            "amount": dto.amount,
        }

        # Generation step
        generate_sig = signature(
            "generate_video",
            args=[dto.video_job_id, dto.format],
        ).set(queue="video.generate")

        # Saga finalization: confirm the charge after successful generation
        confirm_sig = signature(
            "confirm_charge",
            kwargs=billing_kwargs,
        ).set(queue="video.billing")

        # Saga compensation: release reservation on failure
        compensate_sig = signature(
            "compensate_failed_job",
            kwargs=billing_kwargs,
        ).set(queue="video.billing")

        # Build the pipeline
        #
        # publish_video is attached as a success callback (link) rather than
        # as part of the chain so that a publishing failure does NOT trigger
        # the compensation task — the charge has already been confirmed at
        # that point and must not be reversed.
        pipeline = chain(generate_sig, confirm_sig)

        apply_kwargs: dict = {"link_error": compensate_sig}

        if dto.platform is not None:
            publish_sig = signature(
                "publish_video",
                kwargs={
                    "user_id": dto.user_id,
                    "platform": dto.platform.value,
                    "metadata": dto.metadata,
                },
            ).set(queue="video.publish")
            apply_kwargs["link"] = publish_sig

        pipeline.apply_async(**apply_kwargs)


@lru_cache
def get_video_processor() -> CeleryVideoProcessor:
    return CeleryVideoProcessor()
