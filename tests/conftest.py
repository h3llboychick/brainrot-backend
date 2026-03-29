import pytest
from unittest.mock import AsyncMock, MagicMock
from src.domain.use_cases.auth.login_user_email import LoginUserEmailUseCase
from src.domain.use_cases.auth.refresh_access_token import RefreshAccessTokenUseCase


@pytest.fixture
def mock_user_repository():
    repo = MagicMock()
    repo.get_user_by_email = AsyncMock()
    return repo


@pytest.fixture
def mock_token_service():
    repo = MagicMock()
    return repo


@pytest.fixture
def mock_token_repository():
    repo = MagicMock()
    repo.save_token = AsyncMock()
    repo.is_token_active = AsyncMock()
    return repo


@pytest.fixture
def mock_password_hasher():
    hasher = MagicMock()
    return hasher


@pytest.fixture
def login_user_email_use_case(
    mock_user_repository,
    mock_token_repository,
    mock_token_service,
    mock_password_hasher,
):
    return LoginUserEmailUseCase(
        user_repository=mock_user_repository,
        token_service=mock_token_service,
        token_repository=mock_token_repository,
        password_hasher=mock_password_hasher,
    )


@pytest.fixture
def refresh_access_token_use_case(mock_token_repository, mock_token_service):
    return RefreshAccessTokenUseCase(
        token_repository=mock_token_repository,
        token_service=mock_token_service,
    )
