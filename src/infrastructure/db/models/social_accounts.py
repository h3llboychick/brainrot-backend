from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.domain.enums import SocialPlatform
from src.infrastructure.db.models.base import Base


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    id: Mapped[str] = mapped_column(
        "social_account_id", default=lambda: str(uuid4()), primary_key=True
    )
    owner_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"), nullable=False
    )
    platform_account_id: Mapped[str] = mapped_column(nullable=False, index=True)
    platform = mapped_column(PGEnum(SocialPlatform), nullable=False)
    encrypted_credentials: Mapped[bytes] = mapped_column(nullable=False)
    wrapped_dek: Mapped[bytes] = mapped_column(nullable=False)
    kek_id: Mapped[int] = mapped_column(nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )

    owner: Mapped["User"] = relationship(back_populates="social_accounts")  # noqa: F821, we can't import here due to circular import issues
