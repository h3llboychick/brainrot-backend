from src.domain.dtos.auth import (
    EmailLoginDTO,
    AuthTokenResponseDTO,
    CreateTokenPayloadDTO,
)

from src.domain.entities import RefreshToken
from src.domain.exceptions import (
    InvalidCredentialsError,
    UserNotActiveError,
    UserNotVerifiedError,
    UserNotFoundError,
)
from src.domain.interfaces.repositories import ITokenRepository, IUserRepository
from src.domain.interfaces.services import IPasswordHasher, ITokenService
from src.infrastructure.logging import get_logger

logger = get_logger("app.auth.login_user_email")


class LoginUserEmailUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: ITokenService,
        token_repository: ITokenRepository,
        password_hasher: IPasswordHasher,
    ):
        self.user_repository = user_repository
        self.token_service = token_service
        self.token_repository = token_repository
        self.password_hasher = password_hasher

    async def execute(self, dto: EmailLoginDTO) -> AuthTokenResponseDTO:
        logger.info(f"Attempting to log in user with email: {dto.email}")

        # Check if user exists
        user = await self.user_repository.get_user_by_email(dto.email)
        if not user:
            logger.warning(f"Login failed: User with email {dto.email} not found")
            raise UserNotFoundError(email=dto.email)

        # Check if user is verified and active
        if not user.is_verified:
            logger.warning(f"Login failed: User with email {dto.email} is not verified")
            raise UserNotVerifiedError()
        if not user.is_active:
            logger.warning(f"Login failed: User with email {dto.email} is not active")
            raise UserNotActiveError()

        if not user.hashed_password:
            logger.warning(
                f"Login failed: User with email {dto.email} does not have a password set"
            )
            raise InvalidCredentialsError()

        # Check if credentials are valid
        if not self.password_hasher.verify_password(dto.password, user.hashed_password):
            logger.warning(
                f"Login failed: Invalid credentials for user with email {dto.email}"
            )
            raise InvalidCredentialsError()

        # Generate access and refresh tokens and save the refresh token to the token repository
        access_token, refresh_token = self.token_service.create_token_pair(
            payload=CreateTokenPayloadDTO(user_id=str(user.id), email=user.email)
        )
        await self.token_repository.save_token(
            token=RefreshToken(
                user_id=str(user.id),
                token=refresh_token.token,
                expires_at=refresh_token.expires_at,
                created_at=refresh_token.created_at,
            )
        )

        # Return the tokens
        logger.info(f"User with email {dto.email} logged in successfully")
        return AuthTokenResponseDTO(
            access_token=access_token, refresh_token=refresh_token
        )
