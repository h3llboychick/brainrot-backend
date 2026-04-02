from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import BalanceTransaction
from src.domain.enums import BalanceTransactionType
from src.domain.interfaces.repositories import IBalanceLedgerRepository
from src.infrastructure.db.models import (
    BalanceTransaction as BalanceTransactionModel,
)


class BalanceLedgerRepository(IBalanceLedgerRepository):
    def __init__(self, db_session: AsyncSession):
        self._session = db_session

    async def create_transaction(
        self, transaction: BalanceTransaction
    ) -> BalanceTransaction:
        model = BalanceTransactionModel(
            user_id=transaction.user_id,
            job_id=transaction.job_id,
            payment_provider_id=transaction.payment_provider_id,
            type=transaction.type,
            amount=transaction.amount,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return BalanceTransaction.model_validate(model, from_attributes=True)

    async def has_transaction(
        self, job_id: str, transaction_type: BalanceTransactionType
    ) -> bool:
        query = select(BalanceTransactionModel).where(
            BalanceTransactionModel.job_id == job_id,
            BalanceTransactionModel.type == transaction_type,
        )
        result = (await self._session.execute(query)).scalar_one_or_none()
        return result is not None

    async def get_transactions_for_job(
        self, job_id: str
    ) -> list[BalanceTransaction]:
        query = select(BalanceTransactionModel).where(
            BalanceTransactionModel.job_id == job_id
        )
        results = (await self._session.execute(query)).scalars().all()
        return [
            BalanceTransaction.model_validate(r, from_attributes=True)
            for r in results
        ]

    async def has_payment_provider_transaction(
        self, payment_provider_id: str
    ) -> bool:
        query = select(BalanceTransactionModel).where(
            BalanceTransactionModel.payment_provider_id == payment_provider_id
        )
        result = (await self._session.execute(query)).scalar_one_or_none()
        return result is not None
