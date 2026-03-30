from datetime import datetime

from pydantic import BaseModel


class TokenPayloadDTO(BaseModel):
    user_id: str
    jti: str


class TokenDTO(BaseModel):
    token: str
    type: str
    expires_at: datetime
    created_at: datetime
    payload: TokenPayloadDTO


class CreateTokenPayloadDTO(BaseModel):
    user_id: str


class AuthTokenResponseDTO(BaseModel):
    access_token: TokenDTO
    refresh_token: TokenDTO


class RefreshAccessTokenDTO(BaseModel):
    refresh_token: str
