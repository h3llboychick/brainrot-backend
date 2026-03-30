from datetime import datetime, timezone

import pytest

from src.domain.dtos.auth import EmailVerificationDTO
from src.domain.entities import User
from src.domain.exceptions import (
    InvalidVerificationCodeError,
    UserNotFoundError,
    VerificationCodeNotFoundError,
)


# Scenario 1: user not found
@pytest.mark.asyncio
async def test_verify_user_email_user_not_found(
    verify_user_email_use_case, mock_user_repository
):
    mock_user_repository.get_by_email.return_value = None

    dto = EmailVerificationDTO(
        email="user@test.com", verification_code="123456"
    )
    with pytest.raises(UserNotFoundError):
        await verify_user_email_use_case.execute(dto)

    mock_user_repository.get_by_email.assert_called_once_with("user@test.com")


# Scenario 2: verification code not found
@pytest.mark.asyncio
async def test_verify_user_email_verification_code_not_found(
    verify_user_email_use_case,
    mock_user_repository,
    mock_verification_code_repository,
):
    mock_user_repository.get_by_email.return_value = User(
        id="user123",
        email="user@test.com",
        hashed_password="hashedpassword",
        is_active=True,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
    )
    mock_verification_code_repository.get_by_email.return_value = None
    dto = EmailVerificationDTO(
        email="user@test.com", verification_code="123456"
    )

    with pytest.raises(VerificationCodeNotFoundError):
        await verify_user_email_use_case.execute(dto)

    mock_user_repository.get_by_email.assert_called_once_with("user@test.com")
    mock_verification_code_repository.get_by_email.assert_called_once_with(
        "user@test.com"
    )


# Scenario 3: user found but verification code is invalid
@pytest.mark.asyncio
async def test_verify_user_email_invalid_verification_code(
    verify_user_email_use_case,
    mock_user_repository,
    mock_verification_code_repository,
):
    mock_user_repository.get_by_email.return_value = User(
        id="user123",
        email="user@test.com",
        hashed_password="hashedpassword",
        is_active=True,
        is_verified=False,
        created_at=datetime.now(timezone.utc),
    )
    mock_verification_code_repository.get_by_email.return_value = "654321"
    dto = EmailVerificationDTO(
        email="user@test.com", verification_code="123456"
    )

    with pytest.raises(InvalidVerificationCodeError):
        await verify_user_email_use_case.execute(dto)

    mock_user_repository.get_by_email.assert_called_once_with("user@test.com")
    mock_verification_code_repository.get_by_email.assert_called_once_with(
        "user@test.com"
    )
