from src.domain.interfaces.repositories import ISocialAccountsRepository
from src.domain.dtos.social_accounts import DisconnectSocialAccountDTO

from src.infrastructure.logging import get_logger


logger = get_logger("app.social_accounts.disconnect_social_account")


class DisconnectSocialAccountUseCase:
    """
    Generic use case for disconnecting any social media account.

    This use case handles the common logic of removing a social account
    connection from the repository.

    Platform-specific cleanup (like revoking tokens) can be done:
    1. Before calling this use case, OR
    2. In the repository implementation if needed
    """

    def __init__(self, social_accounts_repository: ISocialAccountsRepository):
        self.social_accounts_repository = social_accounts_repository

    async def execute(self, dto: DisconnectSocialAccountDTO) -> None:
        logger.info(
            f"Attempting to disconnect {dto.platform.value} account for user_id: {dto.user_id}"
        )

        account = (
            await self.social_accounts_repository.get_by_owner_and_platform_account_id(
                owner_id=dto.user_id,
                platform_account_id=dto.platform_account_id,
                platform=dto.platform,
            )
        )

        if not account or not account.id:
            logger.warning(
                f"No connected {dto.platform.value} account found for user_id: {dto.user_id}"
            )
            return
        await self.social_accounts_repository.delete_by_id(account.id)

        logger.info(
            f"Successfully disconnected {dto.platform.value} account for user_id: {dto.user_id}"
        )
