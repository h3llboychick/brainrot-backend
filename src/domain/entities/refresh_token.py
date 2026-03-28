from pydantic import BaseModel
from datetime import datetime


class RefreshToken(BaseModel):
    id: str | None = None
    user_id: str
    token: str  # Plain token at domain layer; repository handles hashing
    created_at: datetime
    expires_at: datetime
    revoked: bool = False

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        fields = {
            "id": "refresh_token_id",
        }
