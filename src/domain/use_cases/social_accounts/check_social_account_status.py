import json

from src.domain.dtos.encryption import UnprotectCredentialsDTO
from src.domain.dtos.social_accounts import (
    CheckSocialAccountStatusDTO,
)
from src.domain.exceptions import (
    PlatformValidatorNotFoundError,
    SocialAccountNotFoundError,
)
from src.domain.interfaces.repositories import ISocialAccountsRepository
from src.domain.interfaces.services import (
    ICredentialsProtector,
    ISocialAccountValidator,
)
from src.infrastructure.logging import get_logger

logger = get_logger("app.social_accounts.check_social_account_status")


class CheckSocialAccountStatusUseCase:
    def __init__(
        self,
        social_accounts_repository: ISocialAccountsRepository,
        credentials_protector: ICredentialsProtector,
        validator: ISocialAccountValidator | None = None,
    ):
        self.social_accounts_repository = social_accounts_repository
        self.credentials_protector = credentials_protector
        self.validator = validator

    async def execute(self, dto: CheckSocialAccountStatusDTO) -> None:
        if not self.validator:
            logger.error(
                f"No validator configured for platform: {dto.platform.value}"
            )
            raise PlatformValidatorNotFoundError(platform=dto.platform.value)
        platform_name = dto.platform.value
        logger.info(
            f"Checking {platform_name} account status for user_id: {dto.user_id}"
        )

        # Retrieve encrypted account
        social_account = await self.social_accounts_repository.get_by_owner_and_platform_account_id(
            owner_id=dto.user_id,
            platform=dto.platform,
            platform_account_id=dto.platform_account_id,
        )

        if not social_account:
            logger.warning(
                f"No connected {platform_name} account found for user_id: {dto.user_id}"
            )
            raise SocialAccountNotFoundError(
                f"No connected {platform_name} account found"
            )

        logger.info(
            f"Found connected {platform_name} account for user_id: {dto.user_id}"
        )

        # Decrypt credentials
        logger.debug(
            f"Unprotecting {platform_name} credentials for user_id: {dto.user_id}"
        )
        unprotected_credentials = self.credentials_protector.unprotect(
            UnprotectCredentialsDTO(
                ciphertext=social_account.encrypted_credentials,
                wrapped_key=social_account.wrapped_dek,
            )
        )

        credentials_dict = json.loads(
            unprotected_credentials.plaintext.decode("utf-8")
        )

        # Validate credentials using platform-specific validator
        logger.info(
            f"Validating {platform_name} credentials for user_id: {dto.user_id}"
        )
        await self.validator.validate_credentials(credentials_dict)
        logger.info(
            f"{platform_name} credentials are valid for user_id: {dto.user_id}"
        )
