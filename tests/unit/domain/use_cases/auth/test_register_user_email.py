from datetime import datetime, timezone

import pytest

from src.domain.dtos.auth import EmailRegistrationDTO
from src.domain.entities import User
from src.domain.exceptions import UserAlreadyExistsError


# Scenario 1: user already exists
@pytest.mark.asyncio
async def test_register_user_email_user_already_exists(
    register_user_email_use_case, mock_user_repository
):
    mock_user_repository.get_by_email.return_value = User(
        id="user123",
        email="user@test.com",
        hashed_password="hashedpassword",
        is_active=True,
        is_verified=True,
        created_at=datetime.now(timezone.utc),
    )

    dto = EmailRegistrationDTO(email="user@test.com", password="password123")
    with pytest.raises(UserAlreadyExistsError):
        await register_user_email_use_case.execute(dto)
    mock_user_repository.get_by_email.assert_called_once_with(
        email="user@test.com"
    )


# Scenario 2: successful registration
@pytest.mark.asyncio
async def test_register_user_email_success(
    register_user_email_use_case,
    mock_user_repository,
    mock_password_hasher,
):
    dto = EmailRegistrationDTO(email="test@example.com", password="password123")
    mock_user_repository.get_by_email.return_value = None
    mock_password_hasher.hash_password.return_value = "hashedpassword"
    await register_user_email_use_case.execute(dto)
    mock_user_repository.get_by_email.assert_called_once_with(
        email="test@example.com"
    )
    mock_password_hasher.hash_password.assert_called_once_with("password123")
