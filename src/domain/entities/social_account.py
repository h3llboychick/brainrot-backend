from datetime import datetime

from pydantic import BaseModel


class SocialAccount(BaseModel):
    id: str | None = None
    owner_id: str
    platform_account_id: str
    platform: str
    encrypted_credentials: bytes
    wrapped_dek: bytes
    kek_id: int = 1
    created_at: datetime
