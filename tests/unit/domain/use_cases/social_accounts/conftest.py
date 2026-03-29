from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.use_cases.social_accounts.check_social_account_status import (
    CheckSocialAccountStatusUseCase,
)
from src.domain.use_cases.social_accounts.connect_social_account import (
    ConnectSocialAccountUseCase,
)
from src.domain.use_cases.social_accounts.disconnect_social_account import (
    DisconnectSocialAccountUseCase,
)
from src.domain.use_cases.social_accounts.list_social_accounts import (
    ListSocialAccountsUseCase,
)


@pytest.fixture
def mock_social_accounts_repository():
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.update = AsyncMock()
    repo.delete_by_id = AsyncMock()
    repo.list_by_owner = AsyncMock()
    repo.get_by_owner_and_platform_account_id = AsyncMock()
    repo.get_by_id = AsyncMock()
    return repo


@pytest.fixture
def mock_credentials_protector():
    protector = MagicMock()
    return protector


@pytest.fixture
def mock_social_account_validator():
    validator = MagicMock()
    validator.validate_credentials = AsyncMock()
    return validator


@pytest.fixture
def connect_social_account_use_case(
    mock_social_accounts_repository,
    mock_credentials_protector,
):
    return ConnectSocialAccountUseCase(
        social_accounts_repository=mock_social_accounts_repository,
        credentials_protector=mock_credentials_protector,
    )


@pytest.fixture
def disconnect_social_account_use_case(mock_social_accounts_repository):
    return DisconnectSocialAccountUseCase(
        social_accounts_repository=mock_social_accounts_repository,
    )


@pytest.fixture
def check_social_account_status_use_case(
    mock_social_accounts_repository,
    mock_credentials_protector,
    mock_social_account_validator,
):
    return CheckSocialAccountStatusUseCase(
        social_accounts_repository=mock_social_accounts_repository,
        credentials_protector=mock_credentials_protector,
        validator=mock_social_account_validator,
    )


@pytest.fixture
def check_social_account_status_use_case_no_validator(
    mock_social_accounts_repository,
    mock_credentials_protector,
):
    return CheckSocialAccountStatusUseCase(
        social_accounts_repository=mock_social_accounts_repository,
        credentials_protector=mock_credentials_protector,
        validator=None,
    )


@pytest.fixture
def list_social_accounts_use_case(mock_social_accounts_repository):
    return ListSocialAccountsUseCase(
        social_accounts_repository=mock_social_accounts_repository,
    )
