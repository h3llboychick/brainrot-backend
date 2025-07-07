from pathlib import Path
from typing import Dict, Any

from celery import shared_task
from celery.utils.log import get_task_logger

from ..settings import settings as worker_settings

from ..domain.service_container import ServiceContainer
from ..services.video_formats.registry import VideoFormatRegistry
from ..services.event_publisher import get_event_publisher
from ..services.voiceover_service import get_voiceover_generation_service
from ..services.video_storage_manager import get_video_storage_manager

from ..clients.ai import get_ai_client
from ..clients.minio import get_minio_client
from ..clients.elevenlabs import get_elevenlabs_client
from ..clients.pexels import get_pexels_client
from ..clients.redis import get_redis_client


logger = get_task_logger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    queue="video.generate",
    name="generate_video"
)
def generate_video(
    self,
    job_id: str,
    format_name: str,
    format_settings: Dict[str, Any] = None
) -> str:
    format_settings = format_settings or {}
    
    logger.info(f"Starting video generation: job_id={job_id}, format={format_name}")
    
    # Get format implementation
    try:
        format_strategy = VideoFormatRegistry.get_format(format_name)
    except ValueError as e:
        logger.error(f"Invalid format: {e}")
        raise
    
    # Setup workspace
    base_dir = Path(worker_settings.TEMP_BASE_DIR)
    base_dir.mkdir(parents=True, exist_ok=True)
    workspace_root = format_strategy.setup_workspace(job_id, base_dir)
    
    logger.info(f"Workspace created: {workspace_root}")

    # Initialize clients for services
    ai_client = get_ai_client()
    minio_client = get_minio_client()
    elevenlabs_client = get_elevenlabs_client()
    redis_client = get_redis_client()
    pexels_client = get_pexels_client()

    # Initialize event publisher
    event_publisher = get_event_publisher(redis_client)

    # Setup service container
    services = ServiceContainer()
    
    # Register all available services
    services.register('ai_client', ai_client)
    services.register('voiceover', get_voiceover_generation_service(elevenlabs_client))
    services.register('elevenlabs', elevenlabs_client)
    services.register('event_publisher', event_publisher)
    services.register('minio', minio_client)
    services.register('pexels', pexels_client)
    services.register('video_storage_manager', get_video_storage_manager(minio_client))

    logger.info(f"Registered services: {services.list_services()}")

    # Check required services
    required = format_strategy.required_services
    missing = [svc for svc in required if not services.has(svc)]
    if missing:
        logger.error(f"Format '{format_name}' requires missing services: {missing}")
        format_strategy.cleanup_workspace(workspace_root)
        raise ValueError(f"Missing required services for format '{format_name}': {missing}")
    
    try:
        # Generate video (format controls everything)
        logger.info(f"Starting generation for format {format_name}")
        video_url = format_strategy.generate(
            job_id=job_id,
            workspace_root=workspace_root,
            format_settings=format_settings,
            services=services
        )

        logger.info(f"Video uploaded successfully: {video_url}")
        
        return job_id
        
    except Exception as e:
        logger.error(f"Video generation failed for job_id={job_id}: {e}", exc_info=True)
        
        # Publish failure event
        event_publisher.publish_event(
            job_id,
            "failed",
            error=str(e),
            format=format_name
        )
        raise
        
    finally:
        # Always cleanup workspace
        try:
            format_strategy.cleanup_workspace(workspace_root)
            logger.info(f"Workspace cleaned up: {workspace_root}")
        except Exception as e:
            logger.warning(f"Failed to cleanup workspace: {e}")
