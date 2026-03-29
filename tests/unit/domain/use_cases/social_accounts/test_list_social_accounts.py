import pytest

from src.domain.dtos.social_accounts import ListSocialAccountsDTO
from src.domain.entities import SocialAccount
from datetime import datetime, timezone


# Scenario 1: user has no connected accounts
@pytest.mark.asyncio
async def test_list_social_accounts_empty(
    list_social_accounts_use_case,
    mock_social_accounts_repository,
):
    mock_social_accounts_repository.list_by_owner.return_value = []

    dto = ListSocialAccountsDTO(user_id="user123")
    result = await list_social_accounts_use_case.execute(dto)

    mock_social_accounts_repository.list_by_owner.assert_called_once_with(
        owner_id="user123",
    )
    assert result.total_count == 0
    assert result.accounts == []


# Scenario 2: user has multiple connected accounts
@pytest.mark.asyncio
async def test_list_social_accounts_multiple(
    list_social_accounts_use_case,
    mock_social_accounts_repository,
):
    now = datetime.now(timezone.utc)
    accounts = [
        SocialAccount(
            id="sa_1",
            owner_id="user123",
            platform_account_id="yt_channel_123",
            platform="youtube",
            encrypted_credentials=b"encrypted1",
            wrapped_dek=b"wrapped1",
            created_at=now,
        ),
        SocialAccount(
            id="sa_2",
            owner_id="user123",
            platform_account_id="tt_account_456",
            platform="tiktok",
            encrypted_credentials=b"encrypted2",
            wrapped_dek=b"wrapped2",
            created_at=now,
        ),
    ]
    mock_social_accounts_repository.list_by_owner.return_value = accounts

    dto = ListSocialAccountsDTO(user_id="user123")
    result = await list_social_accounts_use_case.execute(dto)

    mock_social_accounts_repository.list_by_owner.assert_called_once_with(
        owner_id="user123",
    )
    assert result.total_count == 2
    assert len(result.accounts) == 2
    assert result.accounts[0].id == "sa_1"
    assert result.accounts[0].platform == "youtube"
    assert result.accounts[0].platform_account_id == "yt_channel_123"
    assert result.accounts[1].id == "sa_2"
    assert result.accounts[1].platform == "tiktok"
    assert result.accounts[1].platform_account_id == "tt_account_456"
