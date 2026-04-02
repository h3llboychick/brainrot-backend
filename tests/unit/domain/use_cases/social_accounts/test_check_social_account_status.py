import json
from datetime import datetime, timezone

import pytest

from src.domain.dtos.encryption import UnprotectedCredentialsDTO
from src.domain.dtos.social_accounts import CheckSocialAccountStatusDTO
from src.domain.entities import SocialAccount
from src.domain.enums import SocialPlatform
from src.domain.exceptions import (
    PlatformValidatorNotFoundError,
    SocialAccountNotFoundError,
)


# Scenario 1: no validator configured
@pytest.mark.asyncio
async def test_check_social_account_status_no_validator(
    check_social_account_status_use_case_no_validator,
):
    dto = CheckSocialAccountStatusDTO(
        user_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
    )

    with pytest.raises(PlatformValidatorNotFoundError):
        await check_social_account_status_use_case_no_validator.execute(dto)


# Scenario 2: social account not found
@pytest.mark.asyncio
async def test_check_social_account_status_not_found(
    check_social_account_status_use_case,
    mock_social_accounts_repository,
):
    mock_social_accounts_repository.get_by_owner_and_platform_account_id.return_value = None

    dto = CheckSocialAccountStatusDTO(
        user_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
    )

    with pytest.raises(SocialAccountNotFoundError):
        await check_social_account_status_use_case.execute(dto)

    mock_social_accounts_repository.get_by_owner_and_platform_account_id.assert_called_once_with(
        owner_id="user123",
        platform=SocialPlatform.youtube,
        platform_account_id="yt_channel_123",
    )


# Scenario 3: successful status check
@pytest.mark.asyncio
async def test_check_social_account_status_success(
    check_social_account_status_use_case,
    mock_social_accounts_repository,
    mock_credentials_protector,
    mock_social_account_validator,
):
    credentials = {"access_token": "token123", "refresh_token": "refresh123"}
    existing_account = SocialAccount(
        id="sa_123",
        owner_id="user123",
        platform_account_id="yt_channel_123",
        platform="youtube",
        encrypted_credentials=b"encrypted_creds",
        wrapped_dek=b"wrapped_key",
        created_at=datetime.now(timezone.utc),
    )
    mock_social_accounts_repository.get_by_owner_and_platform_account_id.return_value = existing_account
    mock_credentials_protector.unprotect.return_value = (
        UnprotectedCredentialsDTO(
            plaintext=json.dumps(credentials).encode("utf-8"),
        )
    )

    dto = CheckSocialAccountStatusDTO(
        user_id="user123",
        platform_account_id="yt_channel_123",
        platform=SocialPlatform.youtube,
    )
    await check_social_account_status_use_case.execute(dto)

    mock_social_accounts_repository.get_by_owner_and_platform_account_id.assert_called_once_with(
        owner_id="user123",
        platform=SocialPlatform.youtube,
        platform_account_id="yt_channel_123",
    )
    mock_credentials_protector.unprotect.assert_called_once()
    mock_social_account_validator.validate_credentials.assert_called_once_with(
        credentials,
    )
