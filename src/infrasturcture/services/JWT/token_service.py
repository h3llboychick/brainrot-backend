from src.domain.interfaces.repositories.token_respository import ITokenRepository
from src.domain.interfaces.services.token_service import ITokenService
from src.domain.dtos.auth.tokens import (
    TokenDTO, TokenPayloadDTO, CreateTokenPayloadDTO
)
from src.domain.exceptions.tokens import (
    InvalidTokenError, ExpiredTokenError, InvalidTokenPayloadError, InvalidTokenTypeError
)

from .jwt_settings import settings

import jwt

from datetime import datetime, timedelta


class JWTTokenService(ITokenService):
    def __init__(
            self,
            secret_key: str = settings.JWT_SECRET_KEY,
            algorithm: str = settings.JWT_ALGORITHM,
            access_token_expire_minutes: int = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
            refresh_token_expire_days: int = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
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
            "exp": datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes),
        }

        access_token = jwt.encode(
            payload=payload_dict,
            algorithm=self.algorithm,
            key=self.secret_key
        )

        return TokenDTO(
            token=access_token,
            type="access",
            expires_at=payload_dict["exp"],
            created_at=datetime.utcnow()
        )
    
    def _create_refresh_token(self, payload: CreateTokenPayloadDTO) -> TokenDTO:
        payload_dict = {
            "user_id": payload.user_id,
            "email": payload.email,
            "type": "refresh",
            "exp": datetime.utcnow() + timedelta(days=self.refresh_token_expire_days),
        }

        refresh_token = jwt.encode(
            payload=payload_dict,
            algorithm=self.algorithm,
            key=self.secret_key
        )

        return TokenDTO(
            token=refresh_token,
            type="refresh",
            expires_at=payload_dict["exp"],
            created_at=datetime.utcnow()
        )

    def create_token_pair(self, payload: CreateTokenPayloadDTO) -> list[TokenDTO]:
        access_token = self._create_access_token(payload=payload)
        refresh_token = self._create_refresh_token(payload=payload)

        return [
            access_token,
            refresh_token
        ]

    def decode_token(self, token: str) -> TokenPayloadDTO:
        try:
            payload: dict = jwt.decode(
                token,
                self.secret_key,
                self.algorithm
            )
            user_id = payload.get("user_id")
            email = payload.get("email")
            token_type = payload.get("type")

            if not user_id or not email or not token_type:
                raise InvalidTokenPayloadError()

            return TokenPayloadDTO(
                user_id=user_id,
                email=email,
                token_type=token_type
            )
        except jwt.ExpiredSignatureError:
            raise ExpiredTokenError()
        except jwt.InvalidTokenError:
            raise InvalidTokenError()

    def renew_access_token(self, refresh_token: str) -> TokenDTO:
        payload = self.decode_token(refresh_token)

        if payload.token_type != "refresh":
            raise InvalidTokenTypeError()
        payload.token_type = "access"

        creation_payload = CreateTokenPayloadDTO(
            user_id=payload.user_id,
            email=payload.email
        )
        new_access_token = self._create_access_token(
            payload=creation_payload
        )
        return new_access_token
    
token_service = JWTTokenService()

