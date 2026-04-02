from src.domain.dtos.videos import (
    VideoGenerationRequestDTO,
    VideoGenerationResponseDTO,
    VideoProcessingRequestDTO,
)
from src.domain.entities import BalanceTransaction, VideoJob
from src.domain.enums import BalanceTransactionType, VideoJobStatus
from src.domain.exceptions import UserNotFoundError, VideoFormatNotFoundError
from src.domain.interfaces.repositories import (
    IBalanceLedgerRepository,
    IUserRepository,
    IVideoRepository,
)
from src.domain.interfaces.services import IVideoProcessor
from src.infrastructure.logging import get_logger

logger = get_logger("app.videos.generate_video")


class GenerateVideoUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        video_repository: IVideoRepository,
        balance_ledger_repository: IBalanceLedgerRepository,
        video_processor: IVideoProcessor,
    ):
        self.user_repository = user_repository
        self.video_repository = video_repository
        self.balance_ledger_repository = balance_ledger_repository
        self.video_processor = video_processor

    async def execute(
        self, dto: VideoGenerationRequestDTO
    ) -> VideoGenerationResponseDTO:
        logger.info(f"Received video generation request: {dto.prompt}")

        # Validate user
        user = await self.user_repository.get_by_id(user_id=dto.user_id)
        if not user:
            logger.error(f"User with ID {dto.user_id} not found.")
            raise UserNotFoundError(user_id=dto.user_id)

        # Validate video format and user balance
        video_format = await self.video_repository.get_video_format_by_id(
            format_id=dto.format_id
        )
        if not video_format:
            logger.error(f"Video format with ID {dto.format_id} not found.")
            raise VideoFormatNotFoundError(format_id=dto.format_id)

        user.reserve_balance(video_format.price)
        await self.user_repository.update(user)

        # Create video job and save it to the database
        logger.info(
            f"Creating video job for user ID {user.id} with format ID {video_format.id}"
        )

        try:
            video_job = VideoJob(
                creator_id=user.id,
                format_id=video_format.id,
                status=VideoJobStatus.queued,
            )
            video_job = await self.video_repository.create_video_job(
                video_job=video_job
            )
        except Exception as e:
            logger.error(f"Failed to create video job: {e}")
            user.release_reservation(video_format.price)
            await self.user_repository.update(user)
            raise

        # Record reservation in the balance ledger
        await self.balance_ledger_repository.create_transaction(
            BalanceTransaction(
                user_id=user.id,
                job_id=video_job.id,
                type=BalanceTransactionType.reservation,
                amount=video_format.price,
            )
        )

        # Schedule video generation for background processing
        logger.info(f"Scheduling video generation for job ID {video_job.id}")
        self.video_processor.schedule_generation(
            dto=VideoProcessingRequestDTO(
                video_job_id=video_job.id,
                format=video_format.name,
                platform=dto.platform if dto.platform else None,
                user_id=dto.user_id,
                amount=video_format.price,
            )
        )

        return VideoGenerationResponseDTO(video_job_id=video_job.id)
