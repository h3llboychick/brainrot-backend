from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column

from src.domain.enums import BalanceTransactionType
from src.infrastructure.db.models.base import Base


class BalanceTransaction(Base):
    __tablename__ = "balance_transactions"

    id: Mapped[int] = mapped_column(
        "balance_transaction_id", primary_key=True, autoincrement=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.user_id"), nullable=False, index=True
    )
    job_id: Mapped[str] = mapped_column(
        ForeignKey("video_jobs.video_job_id"), nullable=True, index=True
    )
    payment_provider_id: Mapped[str | None] = mapped_column(
        nullable=True, unique=True, index=True
    )
    type = mapped_column(PGEnum(BalanceTransactionType), nullable=False)
    amount: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
