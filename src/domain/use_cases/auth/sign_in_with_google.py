from datetime import datetime, timezone

from src.domain.dtos.auth import (
    AuthTokenResponseDTO,
    CreateTokenPayloadDTO,
    GoogleSignInDTO,
)
from src.domain.entities import RefreshToken, User
from src.domain.exceptions import InvalidCredentialsError
from src.domain.interfaces.repositories import ITokenRepository, IUserRepository
from src.domain.interfaces.services import ITokenService
from src.infrastructure.logging import get_logger

logger = get_logger("app.auth.sign_in_with_google")


class SignInWithGoogleUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        token_service: ITokenService,
        token_repository: ITokenRepository,
    ):
        self.user_repository = user_repository
        self.token_service = token_service
        self.token_repository = token_repository

    async def execute(self, dto: GoogleSignInDTO) -> AuthTokenResponseDTO:
        logger.info(f"Attempting Google sign-in for email: {dto.email}")

        # Check if user already exists
        user = await self.user_repository.get_by_email(dto.email)
        if user:
            if user.google_id and user.google_id != dto.google_id:
                logger.warning(
                    f"Google sign-in failed: Google ID does not match for email {dto.email}"
                )
                raise InvalidCredentialsError("Google ID does not match")

            access_token, refresh_token = self.token_service.create_token_pair(
                payload=CreateTokenPayloadDTO(
                    user_id=user.id,
                )
            )
            logger.info(
                f"User with email {dto.email} signed in successfully via Google"
            )

            await self.token_repository.save(
                RefreshToken(
                    user_id=str(user.id),
                    token=refresh_token.token,
                    expires_at=refresh_token.expires_at,
                    created_at=refresh_token.created_at,
                )
            )
            return AuthTokenResponseDTO(
                access_token=access_token, refresh_token=refresh_token
            )

        logger.info(
            f"No existing user found for email {dto.email}. Creating new user."
        )

        # Create a new user
        user = User(
            email=dto.email,
            google_id=dto.google_id,
            is_active=True,
            is_verified=True,
            created_at=datetime.now(timezone.utc),
        )

        # Save the user to the database
        user = await self.user_repository.save(user)

        # Generate JWT tokens for the user and return them
        access_token, refresh_token = self.token_service.create_token_pair(
            payload=CreateTokenPayloadDTO(
                user_id=user.id,
            )
        )
        await self.token_repository.save(
            RefreshToken(
                user_id=str(user.id),
                token=refresh_token.token,
                expires_at=refresh_token.expires_at,
                created_at=refresh_token.created_at,
            )
        )

        # Return the tokens
        logger.info(
            f"New user with email {dto.email} created and signed in successfully via Google"
        )
        return AuthTokenResponseDTO(
            access_token=access_token, refresh_token=refresh_token
        )
