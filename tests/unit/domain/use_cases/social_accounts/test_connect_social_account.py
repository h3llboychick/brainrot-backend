import pytest

from src.domain.dtos.social_accounts import ConnectSocialAccountDTO
from src.domain.dtos.encryption import ProtectedCredentialsDTO
from src.domain.entities import SocialAccount
from src.domain.enums import SocialPlatform
from datetime import datetime, timezone


# Scenario 1: successful connection of a new account
@pytest.mark.asyncio
async def test_connect_social_account_new_account(
    connect_social_account_use_case,
    mock_social_accounts_repository,
    mock_credentials_protector,
):
    mock_credentials_protector.protect.return_value = ProtectedCredentialsDTO(
        ciphertext=b"encrypted_creds",
        wrapped_key=b"wrapped_key",
    )
    mock_social_accounts_repository.get_by_owner_and_platform_account_id.return_value = None

    dto = ConnectSocialAccountDTO(
        user_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
        credentials={"access_token": "token123"},
    )
    result = await connect_social_account_use_case.execute(dto)

    mock_credentials_protector.protect.assert_called_once()
    mock_social_accounts_repository.get_by_owner_and_platform_account_id.assert_called_once_with(
        owner_id="user123",
        platform=SocialPlatform.youtube,
        platform_account_id="yt_channel_123",
    )
    mock_social_accounts_repository.save.assert_called_once()
    mock_social_accounts_repository.update.assert_not_called()

    assert result.platform == SocialPlatform.youtube
    assert "connected successfully" in result.message


# Scenario 2: account already exists (should update)
@pytest.mark.asyncio
async def test_connect_social_account_existing_account_updates(
    connect_social_account_use_case,
    mock_social_accounts_repository,
    mock_credentials_protector,
):
    mock_credentials_protector.protect.return_value = ProtectedCredentialsDTO(
        ciphertext=b"new_encrypted_creds",
        wrapped_key=b"new_wrapped_key",
    )
    existing_account = SocialAccount(
        id="sa_123",
        owner_id="user123",
        platform_account_id="yt_channel_123",
        platform="youtube",
        encrypted_credentials=b"old_encrypted_creds",
        wrapped_dek=b"old_wrapped_key",
        created_at=datetime.now(timezone.utc),
    )
    mock_social_accounts_repository.get_by_owner_and_platform_account_id.return_value = existing_account

    dto = ConnectSocialAccountDTO(
        user_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
        credentials={"access_token": "new_token"},
    )
    result = await connect_social_account_use_case.execute(dto)

    mock_credentials_protector.protect.assert_called_once()
    mock_social_accounts_repository.update.assert_called_once_with(
        social_account=existing_account,
    )
    mock_social_accounts_repository.save.assert_not_called()

    assert existing_account.encrypted_credentials == b"new_encrypted_creds"
    assert existing_account.wrapped_dek == b"new_wrapped_key"
    assert result.platform == SocialPlatform.youtube
    assert "updated successfully" in result.message
