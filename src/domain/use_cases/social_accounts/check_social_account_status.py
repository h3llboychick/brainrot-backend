from src.domain.interfaces.repositories.social_accounts_repository import ISocialAccountsRepository
from src.domain.interfaces.services.credentials_protector import ICredentialsProtector
from src.domain.interfaces.services.social_account_validator import ISocialAccountValidator

from src.domain.dtos.social_accounts.base import CheckSocialAccountStatusDTO, SocialAccountStatusDTO
from src.domain.dtos.encryption.encryption import UnprotectCredentialsDTO

from src.domain.exceptions.account_validation import NotFoundSocialAccountError

from src.infrastructure.logging.logger import get_logger

import json


logger = get_logger("app.social_accounts.check_social_account_status")


class CheckSocialAccountStatusUseCase:
    def __init__(
        self,
        social_accounts_repository: ISocialAccountsRepository,
        credentials_protector: ICredentialsProtector,
        validator: ISocialAccountValidator
    ):
        self.social_accounts_repository = social_accounts_repository
        self.credentials_protector = credentials_protector
        self.validator = validator

    async def execute(self, dto: CheckSocialAccountStatusDTO) -> SocialAccountStatusDTO:
        platform_name = dto.platform.value
        logger.info(f"Checking {platform_name} account status for user_id: {dto.user_id}")

        # Retrieve encrypted account
        social_account = await self.social_accounts_repository.get_by_owner_and_platform_account_id(
            owner_id=dto.user_id,
            platform=dto.platform.value,
            platform_account_id=dto.platform_account_id
        )

        if not social_account:
            logger.warning(f"No connected {platform_name} account found for user_id: {dto.user_id}")
            raise NotFoundSocialAccountError(f"No connected {platform_name} account found") 

        logger.info(f"Found connected {platform_name} account for user_id: {dto.user_id}")
        
        # Decrypt credentials
        logger.debug(f"Unprotecting {platform_name} credentials for user_id: {dto.user_id}")
        unprotected_credentials = self.credentials_protector.unprotect(
            UnprotectCredentialsDTO(
                ciphertext=social_account.encrypted_credentials,
                wrapped_key=social_account.wrapped_dek
            )
        )
        
        credentials_dict = json.loads(unprotected_credentials.plaintext.decode('utf-8'))
        
        # Validate credentials using platform-specific validator
        logger.info(f"Validating {platform_name} credentials for user_id: {dto.user_id}")
        await self.validator.validate_credentials(credentials_dict)
        logger.info(f"{platform_name} credentials are valid for user_id: {dto.user_id}")

        
