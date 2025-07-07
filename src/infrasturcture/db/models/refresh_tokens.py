from src.infrasturcture.db.models.base import Base

from sqlalchemy import func, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from datetime import datetime


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    id: Mapped[int] = mapped_column("refresh_token_id", primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    hashed_token: Mapped[str] = mapped_column(unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=func.now(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(nullable=False)
    revoked: Mapped[bool] = mapped_column(default=False, nullable=False)
