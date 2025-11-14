from src.domain.entities.social_account import SocialAccount
from src.domain.interfaces.repositories.social_accounts_repository import ISocialAccountsRepository
from src.domain.interfaces.services.credentials_protector import ICredentialsProtector

from src.domain.dtos.social_accounts.base import ConnectSocialAccountDTO, ConnectSocialAccountResponseDTO
from src.domain.dtos.encryption.encryption import ProtectCredentialsDTO

from src.infrastructure.logging.logger import get_logger

from datetime import datetime
import json


logger = get_logger("app.social_accounts.connect_social_account")


class ConnectSocialAccountUseCase:
    """
    Generic use case for connecting any social media account.
    
    This use case handles the common logic of:
    1. Protecting (encrypting) the credentials
    2. Storing the social account connection in the repository
    
    Platform-specific validation should be done before calling this use case.
    """
    
    def __init__(
        self,
        social_accounts_repository: ISocialAccountsRepository,
        credentials_protector: ICredentialsProtector
    ):
        self.social_accounts_repository = social_accounts_repository
        self.credentials_protector = credentials_protector

    async def execute(self, dto: ConnectSocialAccountDTO) -> ConnectSocialAccountResponseDTO:
        logger.info(
            f"Attempting to connect {dto.platform.value} account for user_id: {dto.user_id}"
        )

        logger.debug(
            f"Protecting {dto.platform.value} credentials for user_id: {dto.user_id}"
        )
        protected_credentials = self.credentials_protector.protect(
            ProtectCredentialsDTO(
                plaintext=json.dumps(dto.credentials).encode('utf-8')
            )
        )

        # Check if account already exists to prevent duplicates
        existing_account = await self.social_accounts_repository.get_by_owner_and_platform_account_id(
            owner_id=dto.user_id,
            platform=dto.platform,
            platform_account_id=dto.platform_account_id
        )
        if existing_account:
            logger.info("Account already connected, updating existing record instead.")
            existing_account.encrypted_credentials = protected_credentials.ciphertext
            existing_account.wrapped_dek = protected_credentials.wrapped_key
            await self.social_accounts_repository.update(
                social_account=existing_account
            )

            logger.info("Account successfully updated.")
            return ConnectSocialAccountResponseDTO(
                message=f"{dto.platform.value} account updated successfully.",
                platform=dto.platform,
                connected_at=datetime.utcnow()
            )
        else:
            await self.social_accounts_repository.create(
                SocialAccount(
                    owner_id=dto.user_id,
                    platform=dto.platform.value,
                    platform_account_id=dto.platform_account_id,
                    encrypted_credentials=protected_credentials.ciphertext,
                    wrapped_dek=protected_credentials.wrapped_key,
                    created_at=datetime.utcnow()
                )
            )

            logger.info(f"Successfully connected {dto.platform.value} account for user_id: {dto.user_id}")
            return ConnectSocialAccountResponseDTO(
                message=f"{dto.platform.value} account connected successfully.",
                platform=dto.platform,
                connected_at=datetime.utcnow()
            )
