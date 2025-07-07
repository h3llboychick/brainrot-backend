from .base import Base

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

from datetime import datetime
from uuid import uuid4

import enum

class SocialPlatform(enum.Enum):
    youtube = "youtube"
    twitch = "tiktok"
    instagram = "instagram"

class SocialAccount(Base):
    __tablename__ = "social_accounts"
    
    id: Mapped[str] = mapped_column("social_account_id", default=str(uuid4()), primary_key=True)
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    platform = mapped_column(PGEnum(SocialPlatform), nullable=False)
    encrypted_credentials: Mapped[bytes] = mapped_column(nullable=False)
    wrapped_dek: Mapped[bytes] = mapped_column(nullable=False)
    kek_id: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)