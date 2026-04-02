from abc import ABC, abstractmethod

from src.domain.entities import BalanceTransaction
from src.domain.enums import BalanceTransactionType


class IBalanceLedgerRepository(ABC):
    @abstractmethod
    async def create_transaction(
        self, transaction: BalanceTransaction
    ) -> BalanceTransaction:
        """Record a balance transaction in the ledger."""
        pass

    @abstractmethod
    async def has_transaction(
        self, job_id: str, transaction_type: BalanceTransactionType
    ) -> bool:
        """Check if a transaction of the given type already exists for a job (idempotency)."""
        pass

    @abstractmethod
    async def get_transactions_for_job(
        self, job_id: str
    ) -> list[BalanceTransaction]:
        """Retrieve all balance transactions for a given job."""
        pass

    @abstractmethod
    async def has_payment_provider_transaction(
        self, payment_provider_id: str
    ) -> bool:
        """Check if a transaction with this payment provider ID already exists (idempotency)."""
        pass
