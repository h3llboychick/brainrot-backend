from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.use_cases.auth.login_user_email import LoginUserEmailUseCase
from src.domain.use_cases.auth.refresh_access_token import (
    RefreshAccessTokenUseCase,
)
from src.domain.use_cases.auth.register_user_email import (
    RegisterUserEmailUseCase,
)
from src.domain.use_cases.auth.sign_in_with_google import (
    SignInWithGoogleUseCase,
)
from src.domain.use_cases.auth.verify_user_email import VerifyUserEmailUseCase


@pytest.fixture
def mock_user_repository():
    repo = MagicMock()
    repo.get_by_email = AsyncMock()
    repo.save = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_token_service():
    repo = MagicMock()
    return repo


@pytest.fixture
def mock_token_repository():
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.is_active = AsyncMock()
    return repo


@pytest.fixture
def mock_password_hasher():
    hasher = MagicMock()
    return hasher


@pytest.fixture
def mock_verification_code_repository():
    repo = MagicMock()
    repo.save = AsyncMock()
    repo.delete = AsyncMock()
    repo.get_by_email = AsyncMock()
    return repo


@pytest.fixture
def mock_email_service():
    service = MagicMock()
    service.send_verification_email = MagicMock()
    return service


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


@pytest.fixture
def register_user_email_use_case(
    mock_user_repository,
    mock_verification_code_repository,
    mock_email_service,
    mock_password_hasher,
):
    return RegisterUserEmailUseCase(
        user_repository=mock_user_repository,
        verification_code_repository=mock_verification_code_repository,
        email_service=mock_email_service,
        password_hasher=mock_password_hasher,
    )


@pytest.fixture
def sign_in_with_google_use_case(
    mock_user_repository,
    mock_token_repository,
    mock_token_service,
):
    return SignInWithGoogleUseCase(
        user_repository=mock_user_repository,
        token_service=mock_token_service,
        token_repository=mock_token_repository,
    )


@pytest.fixture
def verify_user_email_use_case(
    mock_user_repository,
    mock_verification_code_repository,
    mock_email_service,
):
    return VerifyUserEmailUseCase(
        user_repository=mock_user_repository,
        verification_code_repository=mock_verification_code_repository,
        email_service=mock_email_service,
    )
