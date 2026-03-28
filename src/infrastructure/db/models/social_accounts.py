from src.domain.enums import SocialPlatform
from src.infrastructure.db.models.base import Base

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy.dialects.postgresql import ENUM as PGEnum

from datetime import datetime
from uuid import uuid4


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id: Mapped[str] = mapped_column(
        "social_account_id", default=lambda: str(uuid4()), primary_key=True
    )
    owner_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    platform_account_id: Mapped[str] = mapped_column(nullable=False, index=True)
    platform = mapped_column(PGEnum(SocialPlatform), nullable=False)
    encrypted_credentials: Mapped[bytes] = mapped_column(nullable=False)
    wrapped_dek: Mapped[bytes] = mapped_column(nullable=False)
    kek_id: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)

    owner: Mapped["User"] = relationship(back_populates="social_accounts")  # noqa: F821, we can't import here due to circular import issues
