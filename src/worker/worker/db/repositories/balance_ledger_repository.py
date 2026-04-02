from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models.balance_transaction import (
    BalanceTransaction,
    BalanceTransactionType,
)


class BalanceLedgerRepository:
    def __init__(self, session: Session):
        self._session = session

    def has_transaction(
        self, job_id: str, transaction_type: BalanceTransactionType
    ) -> bool:
        """Check if a transaction of the given type already exists (idempotency)."""
        result = self._session.execute(
            select(BalanceTransaction).where(
                BalanceTransaction.job_id == job_id,
                BalanceTransaction.type == transaction_type,
            )
        ).scalar_one_or_none()
        return result is not None

    def create_transaction(
        self,
        user_id: str,
        job_id: str,
        transaction_type: BalanceTransactionType,
        amount: float,
    ) -> BalanceTransaction:
        """Record a balance transaction in the ledger."""
        entry = BalanceTransaction(
            user_id=user_id,
            job_id=job_id,
            type=transaction_type,
            amount=amount,
        )
        self._session.add(entry)
        return entry
