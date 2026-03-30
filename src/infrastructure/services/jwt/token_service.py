import uuid
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import jwt

from src.domain.dtos.auth import (
    CreateTokenPayloadDTO,
    TokenDTO,
    TokenPayloadDTO,
)
from src.domain.enums import TokenType
from src.domain.exceptions import (
    ExpiredTokenError,
    InvalidTokenError,
    InvalidTokenPayloadError,
    InvalidTokenTypeError,
)
from src.domain.interfaces.services import ITokenService

from .jwt_settings import get_settings


class JWTTokenService(ITokenService):
    def __init__(self):
        s = get_settings()
        self.secret_key = s.JWT_SECRET_KEY
        self.algorithm = s.JWT_ALGORITHM
        self.access_token_expire_minutes = s.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = s.JWT_REFRESH_TOKEN_EXPIRE_DAYS

    def _create_access_token(self, payload: CreateTokenPayloadDTO) -> TokenDTO:
        jti = str(uuid.uuid4())
        payload_dict = {
            "user_id": payload.user_id,
            "jti": jti,
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
            payload=TokenPayloadDTO(user_id=payload.user_id, jti=jti),
        )

    def _create_refresh_token(self, payload: CreateTokenPayloadDTO) -> TokenDTO:
        jti = str(uuid.uuid4())
        payload_dict = {
            "user_id": payload.user_id,
            "jti": jti,
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
            payload=TokenPayloadDTO(user_id=payload.user_id, jti=jti),
        )

    def create_token_pair(
        self, payload: CreateTokenPayloadDTO
    ) -> tuple[TokenDTO, TokenDTO]:
        access_token = self._create_access_token(payload=payload)
        refresh_token = self._create_refresh_token(payload=payload)

        return access_token, refresh_token

    def decode_token(self, token: str) -> TokenDTO:
        try:
            payload: dict = jwt.decode(
                token, self.secret_key, algorithms=[self.algorithm]
            )
            user_id = payload.get("user_id")
            jti = payload.get("jti")
            token_type = payload.get("type")

            if not user_id or not jti or not token_type:
                raise InvalidTokenPayloadError()

            return TokenDTO(
                token=token,
                type=token_type,
                expires_at=datetime.fromtimestamp(
                    payload["exp"], tz=timezone.utc
                ),
                created_at=datetime.now(tz=timezone.utc),
                payload=TokenPayloadDTO(user_id=user_id, jti=jti),
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


@lru_cache
def get_token_service() -> JWTTokenService:
    return JWTTokenService()
