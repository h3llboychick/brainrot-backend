import pytest
from src.domain.dtos.auth import EmailLoginDTO, TokenDTO
from src.domain.dtos.auth.tokens import TokenPayloadDTO
from src.domain.exceptions import (
    UserNotFoundError,
    UserNotVerifiedError,
    UserNotActiveError,
    InvalidCredentialsError,
)
from src.domain.entities import User
from datetime import datetime, timezone


# Scenario 1: user does not exist
async def test_login_user_email_user_not_found(
    login_user_email_use_case, mock_user_repository
):
    mock_user_repository.get_by_email.return_value = None

    dto = EmailLoginDTO(email="test@example.com", password="password")

    with pytest.raises(UserNotFoundError):
        await login_user_email_use_case.execute(dto)

    mock_user_repository.get_by_email.assert_called_once_with("test@example.com")


# Scenario 2: user is not verified
async def test_login_user_email_user_not_verified(
    login_user_email_use_case, mock_user_repository
):
    mock_user_repository.get_by_email.return_value = User(
        id="user123",
        email="test@example.com",
        is_verified=False,
        is_active=True,
        created_at=datetime.now(timezone.utc),
    )

    dto = EmailLoginDTO(email="test@example.com", password="password")

    with pytest.raises(UserNotVerifiedError):
        await login_user_email_use_case.execute(dto)


# Scenario 3: user is not active
async def test_login_user_email_user_not_active(
    login_user_email_use_case, mock_user_repository
):
    mock_user_repository.get_by_email.return_value = User(
        id="user123",
        email="test@example.com",
        is_verified=True,
        is_active=False,
        created_at=datetime.now(timezone.utc),
    )

    dto = EmailLoginDTO(email="test@example.com", password="password")

    with pytest.raises(UserNotActiveError):
        await login_user_email_use_case.execute(dto)


# Scenario 4: invalid credentials
async def test_login_user_email_invalid_credentials(
    login_user_email_use_case, mock_user_repository, mock_password_hasher
):
    mock_user_repository.get_by_email.return_value = User(
        id="user123",
        email="test@example.com",
        is_verified=True,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        hashed_password="hashedpassword",
    )

    dto = EmailLoginDTO(email="test@example.com", password="wrongpassword")

    mock_password_hasher.verify_password.return_value = False

    with pytest.raises(InvalidCredentialsError):
        await login_user_email_use_case.execute(dto)

    mock_password_hasher.verify_password.assert_called_once_with(
        "wrongpassword", "hashedpassword"
    )


# Scenario 5: successful login
async def test_login_user_email_success(
    login_user_email_use_case,
    mock_user_repository,
    mock_password_hasher,
    mock_token_service,
):
    mock_user_repository.get_by_email.return_value = User(
        id="user123",
        email="test@example.com",
        is_verified=True,
        is_active=True,
        created_at=datetime.now(timezone.utc),
        hashed_password="hashedpassword",
    )

    dto = EmailLoginDTO(email="test@example.com", password="password")
    access_token = TokenDTO(
        token="access_token",
        type="access",
        expires_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        payload=TokenPayloadDTO(user_id="user123", email="test@example.com"),
    )
    refresh_token = TokenDTO(
        token="refresh_token",
        type="refresh",
        expires_at=datetime.now(timezone.utc),
        created_at=datetime.now(timezone.utc),
        payload=TokenPayloadDTO(user_id="user123", email="test@example.com"),
    )
    mock_password_hasher.verify_password.return_value = True
    mock_token_service.create_token_pair.return_value = [
        access_token,
        refresh_token,
    ]

    response = await login_user_email_use_case.execute(dto)
    assert response.access_token.token == "access_token"
    assert response.refresh_token.token == "refresh_token"
