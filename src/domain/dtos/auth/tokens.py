from datetime import datetime

from pydantic import BaseModel


class TokenDTO(BaseModel):
    token: str
    type: str
    expires_at: datetime
    created_at: datetime


class TokenPayloadDTO(BaseModel):
    user_id: str
    email: str
    token_type: str


class CreateTokenPayloadDTO(BaseModel):
    user_id: str
    email: str


class AuthTokenResponseDTO(BaseModel):
    access_token: TokenDTO
    refresh_token: TokenDTO


class RefreshAccessTokenDTO(BaseModel):
    refresh_token: str
