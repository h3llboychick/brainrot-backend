from datetime import datetime, timezone

import pytest

from src.domain.dtos.auth import GoogleSignInDTO, TokenDTO, TokenPayloadDTO
from src.domain.entities import User
from src.domain.exceptions import InvalidCredentialsError


# Scenario 1: user does not exist
@pytest.mark.asyncio
async def test_sign_in_with_google_user_not_found(
    sign_in_with_google_use_case,
    mock_user_repository,
    mock_token_service,
):
    mock_user_repository.get_by_email.return_value = None
    mock_user_repository.save.return_value = User(
        id="user123",
        email="user@gmail.com",
        google_id="google123",
        is_active=True,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
    )
    mock_token_service.create_token_pair.return_value = (
        TokenDTO(
            token="access_token",
            type="access",
            expires_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            payload=TokenPayloadDTO(user_id="user123", jti="test-jti-1"),
        ),
        TokenDTO(
            token="refresh_token",
            type="refresh",
            expires_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            payload=TokenPayloadDTO(user_id="user123", jti="test-jti-2"),
        ),
    )
    dto = GoogleSignInDTO(email="user@gmail.com", google_id="google123")
    result = await sign_in_with_google_use_case.execute(dto)

    mock_user_repository.get_by_email.assert_called_once_with("user@gmail.com")

    assert result.access_token.token == "access_token"
    assert result.refresh_token.token == "refresh_token"


# Scenario 2: user exists but Google ID does not match
@pytest.mark.asyncio
async def test_sign_in_with_google_google_id_mismatch(
    sign_in_with_google_use_case, mock_user_repository
):
    mock_user_repository.get_by_email.return_value = User(
        id="user123",
        email="user@gmail.com",
        google_id="different_google_id",
        is_active=True,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
    )
    dto = GoogleSignInDTO(email="user@gmail.com", google_id="google123")
    with pytest.raises(InvalidCredentialsError):
        await sign_in_with_google_use_case.execute(dto)
    mock_user_repository.get_by_email.assert_called_once_with("user@gmail.com")


# Scenario 3: successful sign-in with existing user
@pytest.mark.asyncio
async def test_sign_in_with_google_success_existing_user(
    sign_in_with_google_use_case, mock_user_repository, mock_token_service
):
    mock_user_repository.get_by_email.return_value = User(
        id="user123",
        email="user@gmail.com",
        google_id="google123",
        is_active=True,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
    )
    mock_token_service.create_token_pair.return_value = (
        TokenDTO(
            token="access_token",
            type="access",
            expires_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            payload=TokenPayloadDTO(user_id="user123", jti="test-jti-1"),
        ),
        TokenDTO(
            token="refresh_token",
            type="refresh",
            expires_at=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc),
            payload=TokenPayloadDTO(user_id="user123", jti="test-jti-2"),
        ),
    )
    dto = GoogleSignInDTO(email="user@gmail.com", google_id="google123")
    result = await sign_in_with_google_use_case.execute(dto)

    mock_user_repository.get_by_email.assert_called_once_with("user@gmail.com")

    assert result.access_token.token == "access_token"
    assert result.refresh_token.token == "refresh_token"
