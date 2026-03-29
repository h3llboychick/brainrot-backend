from src.domain.dtos.auth import EmailVerificationDTO

from src.domain.interfaces.repositories import (
    IUserRepository,
    IVerificationCodeRepository,
)
from src.domain.interfaces.services import IEmailService

from src.domain.exceptions import (
    UserNotFoundError,
    InvalidVerificationCodeError,
    VerificationCodeNotFoundError,
)

from src.infrastructure.logging import get_logger


logger = get_logger("app.auth.verify_user_email")


class VerifyUserEmailUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        verification_code_repository: IVerificationCodeRepository,
        email_service: IEmailService,
    ):
        self.user_repository = user_repository
        self.email_service = email_service
        self.verification_code_repository = verification_code_repository

    async def execute(self, dto: EmailVerificationDTO) -> None:
        logger.info(f"Attempting to verify email for user with email: {dto.email}")

        # Check if user exists
        user = await self.user_repository.get_by_email(dto.email)
        if not user:
            logger.warning(
                f"Email verification failed: User with email {dto.email} not found"
            )
            raise UserNotFoundError(email=dto.email)

        # Retrieve and validate the verification code
        verification_code = await self.verification_code_repository.get_by_email(
            dto.email
        )

        if not verification_code:
            logger.warning(
                f"Email verification failed: No verification code found for email {dto.email}"
            )
            raise VerificationCodeNotFoundError(email=dto.email)

        if not verification_code == dto.verification_code:
            logger.warning(
                f"Email verification failed: Invalid verification code for email {dto.email}"
            )
            raise InvalidVerificationCodeError(email=dto.email)

        # Mark the user as verified and update the user record
        user.is_verified = True
        await self.user_repository.update(user)

        # Delete the used verification code
        await self.verification_code_repository.delete(dto.email)

        logger.info(f"Email verified successfully for user with email: {dto.email}")
