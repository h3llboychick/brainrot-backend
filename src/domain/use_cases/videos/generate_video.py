from src.domain.entities.video_job import VideoJob
from src.domain.enums.video_job_status import VideoJobStatus

from src.domain.dtos.videos.generation import VideoGenerationRequestDTO, VideoGenerationResponseDTO
from src.domain.dtos.videos.processing import VideoProcessingRequestDTO
from src.domain.interfaces.repositories.video_repository import IVideoRepository
from src.domain.interfaces.repositories.user_repository import IUserRepository
from src.domain.interfaces.services.video_processor import IVideoProcessor

from src.domain.exceptions.db import UserNotFoundError

from src.infrasturcture.logging.logger import get_logger


logger = get_logger("app.videos.generate_video")


class GenerateVideoUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        video_repository: IVideoRepository,
        video_processor: IVideoProcessor
    ):
        self.user_repository = user_repository
        self.video_repository = video_repository
        self.video_processor = video_processor

    async def execute(self, dto: VideoGenerationRequestDTO) -> VideoGenerationResponseDTO:
        logger.info(f"Received video generation request: {dto.prompt}")

        # Validate user and format
        user = await self.user_repository.get_user_by_id(user_id=dto.user_id)
        if not user:
            logger.error(f"User with ID {dto.user_id} not found.")
            raise UserNotFoundError(user_id=dto.user_id)

        # Validate video format and user balance
        video_format = await self.video_repository.get_video_format_by_id(format_id=dto.format_id)
        if not video_format:
            logger.error(f"Video format with ID {dto.format_id} not found.")
            raise ValueError("Invalid video format ID")
        
        # Check user balance and deduct price
        if user.balance < video_format.price:
            logger.error(f"User with ID {dto.user_id} has insufficient balance.")
            raise ValueError("Insufficient balance")
        user.deduct_balance(video_format.price)
        await self.user_repository.update_user(user)

        # Create video job and save it to the database
        logger.info(f"Creating video job for user ID {user.id} with format ID {video_format.id}")
        video_job = VideoJob(
            creator_id=user.id,
            format_id=video_format.id,
            status=VideoJobStatus.queued,
        )
        video_job = await self.video_repository.create_video_job(video_job=video_job)

        # Schedule video generation for background processing
        logger.info(f"Scheduling video generation for job ID {video_job.id}")
        self.video_processor.schedule_generation(
            dto=VideoProcessingRequestDTO(
                video_job_id=video_job.id,
                format=video_format.name,
                platform=dto.platform,
                user_id=dto.user_id
            )
        )

        return VideoGenerationResponseDTO(
            video_job_id=video_job.id
        )