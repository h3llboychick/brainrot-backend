from datetime import datetime, timezone

from pydantic import BaseModel, Field

from src.domain.enums import BalanceTransactionType


class BalanceTransaction(BaseModel):
    id: int | None = None
    user_id: str
    job_id: str | None = None
    payment_provider_id: str | None = None
    type: BalanceTransactionType
    amount: float
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
