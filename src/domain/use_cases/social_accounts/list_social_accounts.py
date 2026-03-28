from src.domain.interfaces.repositories import ISocialAccountsRepository
from src.domain.dtos.social_accounts import (
    ListSocialAccountsDTO,
    ListSocialAccountsResponseDTO,
    SocialAccountSummaryDTO,
)

from src.infrastructure.logging import get_logger


logger = get_logger("app.social_accounts.list_social_accounts")


class ListSocialAccountsUseCase:
    """
    Use case for listing all social accounts connected by a user.

    This provides a summary of all connected platforms for display
    in settings or account management pages.
    """

    def __init__(self, social_accounts_repository: ISocialAccountsRepository):
        self.social_accounts_repository = social_accounts_repository

    async def execute(
        self, dto: ListSocialAccountsDTO
    ) -> ListSocialAccountsResponseDTO:
        logger.info(f"Listing all social accounts for user_id: {dto.user_id}")

        accounts = await self.social_accounts_repository.list_by_owner(
            owner_id=dto.user_id
        )

        logger.info(
            f"Found {len(accounts)} connected accounts for user_id: {dto.user_id}"
        )

        # Map to summary DTOs (don't expose credentials)
        account_summaries = [
            SocialAccountSummaryDTO(
                id=account.id,
                platform=account.platform,
                platform_account_id=account.platform_account_id,
                connected_at=account.created_at,
            )
            for account in accounts
        ]

        return ListSocialAccountsResponseDTO(
            accounts=account_summaries, total_count=len(account_summaries)
        )
