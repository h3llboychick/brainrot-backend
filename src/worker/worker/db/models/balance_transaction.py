import enum
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import ENUM as PGEnum
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class BalanceTransactionType(enum.Enum):
    reservation = "reservation"
    confirmation = "confirmation"
    release = "release"
    top_up = "top_up"


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
    type = mapped_column(
        PGEnum(BalanceTransactionType, create_type=False), nullable=False
    )
    amount: Mapped[float] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
