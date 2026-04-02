from typing import Annotated

from fastapi import Depends

from src.domain.use_cases.payments.confirm_top_up import ConfirmTopUpUseCase
from src.infrastructure.db.repositories import (
    BalanceLedgerRepository,
    UserRepository,
)
from src.presentation.di.repositories import (
    get_balance_ledger_repository,
    get_user_repository,
)


def get_confirm_top_up_use_case(
    user_repository: Annotated[UserRepository, Depends(get_user_repository)],
    balance_ledger_repository: Annotated[
        BalanceLedgerRepository, Depends(get_balance_ledger_repository)
    ],
) -> ConfirmTopUpUseCase:
    return ConfirmTopUpUseCase(
        user_repository=user_repository,
        balance_ledger_repository=balance_ledger_repository,
    )
