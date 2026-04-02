from src.domain.entities import BalanceTransaction
from src.domain.enums import BalanceTransactionType
from src.domain.exceptions import UserNotFoundError
from src.domain.interfaces.repositories import (
    IBalanceLedgerRepository,
    IUserRepository,
)
from src.infrastructure.logging import get_logger

logger = get_logger("app.payments.confirm_top_up")


class ConfirmTopUpUseCase:
    def __init__(
        self,
        user_repository: IUserRepository,
        balance_ledger_repository: IBalanceLedgerRepository,
    ):
        self.user_repository = user_repository
        self.balance_ledger_repository = balance_ledger_repository

    async def execute(
        self,
        user_id: str,
        token_count: int,
        payment_provider_id: str,
    ) -> None:
        """
        Credit tokens to a user's balance after a confirmed payment.

        Idempotent: if a transaction with this payment_provider_id already
        exists, the call is a no-op.
        """
        # Idempotency check
        already_processed = await self.balance_ledger_repository.has_payment_provider_transaction(
            payment_provider_id=payment_provider_id,
        )
        if already_processed:
            logger.info(
                f"Payment {payment_provider_id} already processed, skipping."
            )
            return

        # Load and validate user
        user = await self.user_repository.get_by_id(user_id=user_id)
        if not user:
            logger.error(
                f"User {user_id} not found for payment {payment_provider_id}"
            )
            raise UserNotFoundError(user_id=user_id)

        # Credit balance
        user.add_balance(float(token_count))
        await self.user_repository.update(user)

        # Record ledger entry
        await self.balance_ledger_repository.create_transaction(
            BalanceTransaction(
                user_id=user_id,
                payment_provider_id=payment_provider_id,
                type=BalanceTransactionType.top_up,
                amount=float(token_count),
            )
        )

        logger.info(
            f"Credited {token_count} tokens to user {user_id} "
            f"(payment: {payment_provider_id})"
        )
