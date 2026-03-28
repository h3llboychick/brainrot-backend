from src.domain.interfaces.services import ITokenService
from src.domain.interfaces.repositories import ITokenRepository
from src.domain.dtos.auth import RefreshAccessTokenDTO, TokenDTO

from src.domain.exceptions import (
    InvalidTokenError,
    TokenInactiveError,
    TokenNotFoundError,
)

from src.infrastructure.logging import get_logger


logger = get_logger("app.auth.refresh_access_token")


class RefreshAccessTokenUseCase:
    def __init__(
        self, token_repository: ITokenRepository, token_service: ITokenService
    ):
        self.token_repository = token_repository
        self.token_service = token_service

    async def execute(self, dto: RefreshAccessTokenDTO) -> TokenDTO:
        logger.info("Attempting to refresh access token")

        # Validate the refresh token
        token_data = self.token_service.decode_token(dto.refresh_token)

        # Check if the refresh token is active
        try:
            if not await self.token_repository.is_token_active(token=dto.refresh_token):
                logger.warning(
                    f"Refresh token is inactive or revoked for user_id: {token_data.user_id}"
                )
                raise TokenInactiveError()
        except TokenNotFoundError:
            logger.warning(f"Refresh token not found for user_id: {token_data.user_id}")
            raise InvalidTokenError()

        # Generate a new access token and return it
        logger.info(
            f"Refresh token is valid and active, generating new access token for user_id: {token_data.user_id}"
        )
        return self.token_service.renew_access_token(refresh_token=dto.refresh_token)
