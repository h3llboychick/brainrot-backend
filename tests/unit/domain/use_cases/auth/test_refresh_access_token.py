from datetime import datetime, timezone

import pytest

from src.domain.dtos.auth import (
    RefreshAccessTokenDTO,
    TokenDTO,
    TokenPayloadDTO,
)
from src.domain.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenTypeError,
    TokenInactiveError,
)


# Scenario 1: invalid refresh token
@pytest.mark.asyncio
async def test_refresh_access_token_invalid_token(
    refresh_access_token_use_case, mock_token_service
):
    mock_token_service.validate_refresh_token.side_effect = InvalidTokenError()

    dto = RefreshAccessTokenDTO(refresh_token="invalidtoken")

    with pytest.raises(InvalidTokenError):
        await refresh_access_token_use_case.execute(dto)

    mock_token_service.validate_refresh_token.assert_called_once_with(
        "invalidtoken"
    )


# Scenario 2: expired refresh token
@pytest.mark.asyncio
async def test_refresh_access_token_expired_token(
    refresh_access_token_use_case, mock_token_service
):
    mock_token_service.validate_refresh_token.side_effect = ExpiredTokenError()

    dto = RefreshAccessTokenDTO(refresh_token="expiredtoken")

    with pytest.raises(ExpiredTokenError):
        await refresh_access_token_use_case.execute(dto)

    mock_token_service.validate_refresh_token.assert_called_once_with(
        "expiredtoken"
    )


# Scenario 3: inactive refresh token
@pytest.mark.asyncio
async def test_refresh_access_token_inactive_token(
    refresh_access_token_use_case, mock_token_service, mock_token_repository
):
    mock_token_service.validate_refresh_token.return_value = TokenDTO(
        token="inactivetoken",
        type="refresh",
        expires_at=datetime.now(tz=timezone.utc),
        created_at=datetime.now(tz=timezone.utc),
        payload=TokenPayloadDTO(user_id="user123", jti="test-jti"),
    )
    mock_token_repository.is_active.return_value = False

    dto = RefreshAccessTokenDTO(refresh_token="inactivetoken")

    with pytest.raises(TokenInactiveError):
        await refresh_access_token_use_case.execute(dto)

    mock_token_service.validate_refresh_token.assert_called_once_with(
        "inactivetoken"
    )
    mock_token_repository.is_active.assert_called_once_with(
        token="inactivetoken"
    )


# Scenario 4: access token provided instead of refresh token
@pytest.mark.asyncio
async def test_refresh_access_token_access_token_instead_of_refresh_token(
    refresh_access_token_use_case, mock_token_service
):
    mock_token_service.validate_refresh_token.side_effect = (
        InvalidTokenTypeError()
    )

    dto = RefreshAccessTokenDTO(refresh_token="accesstoken")

    with pytest.raises(InvalidTokenTypeError):
        await refresh_access_token_use_case.execute(dto)

    mock_token_service.validate_refresh_token.assert_called_once_with(
        "accesstoken"
    )


# Scenario 5: successful access token refresh
@pytest.mark.asyncio
async def test_refresh_access_token_success(
    refresh_access_token_use_case, mock_token_service, mock_token_repository
):
    mock_token_service.validate_refresh_token.return_value = TokenDTO(
        token="validrefreshtoken",
        type="refresh",
        expires_at=datetime.now(tz=timezone.utc),
        created_at=datetime.now(tz=timezone.utc),
        payload=TokenPayloadDTO(user_id="user123", jti="test-jti-1"),
    )
    mock_token_repository.is_active.return_value = True
    mock_token_service.renew_access_token.return_value = TokenDTO(
        token="newaccesstoken",
        type="access",
        expires_at=datetime.now(tz=timezone.utc),
        created_at=datetime.now(tz=timezone.utc),
        payload=TokenPayloadDTO(user_id="user123", jti="test-jti-2"),
    )

    dto = RefreshAccessTokenDTO(refresh_token="validrefreshtoken")
    result = await refresh_access_token_use_case.execute(dto)

    assert result.token == "newaccesstoken"
    assert result.type == "access"
    assert result.payload.user_id == "user123"
    assert result.payload.jti == "test-jti-2"
