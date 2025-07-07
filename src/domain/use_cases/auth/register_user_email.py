from src.domain.entities.user import User

from src.domain.dtos.auth.registration import EmailRegistrationDTO
from src.domain.dtos.auth.verification import EmailVerificationDTO

from src.domain.interfaces.repositories.user_repository import IUserRepository
from src.domain.interfaces.repositories.verification_code_repository import IVerificationCodeRepository
from src.domain.interfaces.services.email_service import IEmailService
from src.domain.interfaces.services.password_hasher import IPasswordHasher

from src.domain.exceptions.db import UserAlreadyExistsError

from src.infrasturcture.services.email.code_generator import generate_verification_code

from src.infrasturcture.logging.logger import get_logger

from datetime import datetime


logger = get_logger("app.auth.register_user_email")

class RegisterUserEmailUseCase:
    def __init__(
            self, 
            user_repository: IUserRepository,
            verification_code_repository: IVerificationCodeRepository,
            email_service: IEmailService,
            password_hasher: IPasswordHasher
        ):
        self.user_repository = user_repository
        self.verification_code_repository = verification_code_repository
        self.email_service = email_service
        self.password_hasher = password_hasher

    async def execute(self, dto: EmailRegistrationDTO) -> None:
        logger.info(f"Attempting to register user with email: {dto.email}")

        # Check if user already exists
        existing_user = await self.user_repository.get_user_by_email(email=dto.email)
        if existing_user:
            logger.warning(f"Registration failed: User with email {dto.email} already exists")
            raise UserAlreadyExistsError(email=dto.email)

        # Create a new user based on the provided email and password
        hashed_password = self.password_hasher.hash_password(dto.password)
        user = User(
            email=dto.email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,  # Initially not verified
            created_at=datetime.utcnow()
        )

        # Save the user to the database
        user = await self.user_repository.create_user(user)

        # Generate a verification code and save it to verification code repository
        verification_code = generate_verification_code()
        await self.verification_code_repository.save_code(
            email=dto.email,
            code=verification_code
        )

        # Send verification email
        logger.info(f"User with email {dto.email} registered successfully. Sending verification email.")
        self.email_service.send_verification_email(
            EmailVerificationDTO(
                email=dto.email,
                verification_code=verification_code
            )
        )
        