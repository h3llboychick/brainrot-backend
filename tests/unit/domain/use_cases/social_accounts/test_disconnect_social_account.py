import pytest

from src.domain.dtos.social_accounts import DisconnectSocialAccountDTO
from src.domain.entities import SocialAccount
from src.domain.enums import SocialPlatform
from datetime import datetime, timezone


# Scenario 1: successful disconnection
@pytest.mark.asyncio
async def test_disconnect_social_account_success(
    disconnect_social_account_use_case,
    mock_social_accounts_repository,
):
    existing_account = SocialAccount(
        id="sa_123",
        owner_id="user123",
        platform_account_id="yt_channel_123",
        platform="youtube",
        encrypted_credentials=b"encrypted",
        wrapped_dek=b"wrapped",
        created_at=datetime.now(timezone.utc),
    )
    mock_social_accounts_repository.get_by_owner_and_platform_account_id.return_value = existing_account

    dto = DisconnectSocialAccountDTO(
        user_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
    )
    await disconnect_social_account_use_case.execute(dto)

    mock_social_accounts_repository.get_by_owner_and_platform_account_id.assert_called_once_with(
        owner_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
    )
    mock_social_accounts_repository.delete_by_id.assert_called_once_with("sa_123")


# Scenario 2: account not found (no-op)
@pytest.mark.asyncio
async def test_disconnect_social_account_not_found(
    disconnect_social_account_use_case,
    mock_social_accounts_repository,
):
    mock_social_accounts_repository.get_by_owner_and_platform_account_id.return_value = None

    dto = DisconnectSocialAccountDTO(
        user_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
    )
    await disconnect_social_account_use_case.execute(dto)

    mock_social_accounts_repository.get_by_owner_and_platform_account_id.assert_called_once_with(
        owner_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
    )
    mock_social_accounts_repository.delete_by_id.assert_not_called()


# Scenario 3: account exists but has no id (no-op)
@pytest.mark.asyncio
async def test_disconnect_social_account_no_id(
    disconnect_social_account_use_case,
    mock_social_accounts_repository,
):
    account_without_id = SocialAccount(
        id=None,
        owner_id="user123",
        platform_account_id="yt_channel_123",
        platform="youtube",
        encrypted_credentials=b"encrypted",
        wrapped_dek=b"wrapped",
        created_at=datetime.now(timezone.utc),
    )
    mock_social_accounts_repository.get_by_owner_and_platform_account_id.return_value = account_without_id

    dto = DisconnectSocialAccountDTO(
        user_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
    )
    await disconnect_social_account_use_case.execute(dto)

    mock_social_accounts_repository.delete_by_id.assert_not_called()
