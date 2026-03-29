from datetime import datetime, timedelta, timezone

import jwt

from src.domain.dtos.auth import CreateTokenPayloadDTO, TokenDTO, TokenPayloadDTO
from src.domain.enums import TokenType
from src.domain.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenPayloadError,
    InvalidTokenTypeError,
)
from src.domain.interfaces.services import ITokenService

from .jwt_settings import settings


class JWTTokenService(ITokenService):
    def __init__(
        self,
        secret_key: str = settings.JWT_SECRET_KEY,
        algorithm: str = settings.JWT_ALGORITHM,
        access_token_expire_minutes: int = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
        refresh_token_expire_days: int = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
        self.refresh_token_expire_days = refresh_token_expire_days

    def _create_access_token(self, payload: CreateTokenPayloadDTO) -> TokenDTO:
        payload_dict = {
            "user_id": payload.user_id,
            "email": payload.email,
            "type": "access",
            "exp": datetime.now(tz=timezone.utc)
            + timedelta(minutes=self.access_token_expire_minutes),
        }

        access_token = jwt.encode(
            payload=payload_dict, algorithm=self.algorithm, key=self.secret_key
        )

        return TokenDTO(
            token=access_token,
            type="access",
            expires_at=payload_dict["exp"],
            created_at=datetime.now(tz=timezone.utc),
            payload=TokenPayloadDTO(user_id=payload.user_id, email=payload.email),
        )

    def _create_refresh_token(self, payload: CreateTokenPayloadDTO) -> TokenDTO:
        payload_dict = {
            "user_id": payload.user_id,
            "email": payload.email,
            "type": "refresh",
            "exp": datetime.now(tz=timezone.utc)
            + timedelta(days=self.refresh_token_expire_days),
        }

        refresh_token = jwt.encode(
            payload=payload_dict, algorithm=self.algorithm, key=self.secret_key
        )

        return TokenDTO(
            token=refresh_token,
            type="refresh",
            expires_at=payload_dict["exp"],
            created_at=datetime.now(tz=timezone.utc),
            payload=TokenPayloadDTO(user_id=payload.user_id, email=payload.email),
        )

    def create_token_pair(
        self, payload: CreateTokenPayloadDTO
    ) -> tuple[TokenDTO, TokenDTO]:
        access_token = self._create_access_token(payload=payload)
        refresh_token = self._create_refresh_token(payload=payload)

        return access_token, refresh_token

    def decode_token(self, token: str) -> TokenDTO:
        try:
            payload: dict = jwt.decode(token, self.secret_key, self.algorithm)
            user_id = payload.get("user_id")
            email = payload.get("email")
            token_type = payload.get("type")

            if not user_id or not email or not token_type:
                raise InvalidTokenPayloadError()  # do we need

            return TokenDTO(
                token=token,
                type=token_type,
                expires_at=datetime.fromtimestamp(payload["exp"], tz=timezone.utc),
                created_at=datetime.now(tz=timezone.utc),
                payload=TokenPayloadDTO(user_id=user_id, email=email),
            )
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()
        except (jwt.InvalidTokenError, InvalidTokenPayloadError):
            raise InvalidTokenError()

    def _validate_token(self, token: str, expected_type: TokenType) -> TokenDTO:
        token_data = self.decode_token(token)

        if token_data.type != expected_type.value:
            raise InvalidTokenTypeError()

        return token_data

    def validate_access_token(self, token: str) -> TokenDTO:
        return self._validate_token(token, TokenType.ACCESS)

    def validate_refresh_token(self, token: str) -> TokenDTO:
        return self._validate_token(token, TokenType.REFRESH)

    def renew_access_token(self, payload: CreateTokenPayloadDTO) -> TokenDTO:
        return self._create_access_token(payload=payload)


# single instance of the JWTTokenService to be used throughout the application
token_service = JWTTokenService()
