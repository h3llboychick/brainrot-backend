from src.domain.use_cases.social_accounts.connect_social_account import (
    ConnectSocialAccountUseCase,
)
from src.domain.use_cases.social_accounts.disconnect_social_account import (
    DisconnectSocialAccountUseCase,
)
from src.domain.use_cases.social_accounts.list_social_accounts import (
    ListSocialAccountsUseCase,
)
from src.domain.interfaces.repositories import ISocialAccountsRepository
from src.domain.interfaces.services import ICredentialsProtector
from src.domain.use_cases.social_accounts.check_social_account_status import (
    CheckSocialAccountStatusUseCase,
)

from src.presentation.di.repositories import get_social_accounts_repository
from src.presentation.di.services import get_credentials_protector

from fastapi import Depends
from typing import Annotated


def get_connect_social_account_use_case(
    social_accounts_repository: Annotated[
        ISocialAccountsRepository, Depends(get_social_accounts_repository)
    ],
    credentials_protector: Annotated[
        ICredentialsProtector, Depends(get_credentials_protector)
    ],
) -> ConnectSocialAccountUseCase:
    return ConnectSocialAccountUseCase(
        social_accounts_repository=social_accounts_repository,
        credentials_protector=credentials_protector,
    )


def get_disconnect_social_account_use_case(
    social_accounts_repository: Annotated[
        ISocialAccountsRepository, Depends(get_social_accounts_repository)
    ],
) -> DisconnectSocialAccountUseCase:
    return DisconnectSocialAccountUseCase(
        social_accounts_repository=social_accounts_repository
    )


def get_list_social_accounts_use_case(
    social_accounts_repository: Annotated[
        ISocialAccountsRepository, Depends(get_social_accounts_repository)
    ],
) -> ListSocialAccountsUseCase:
    return ListSocialAccountsUseCase(
        social_accounts_repository=social_accounts_repository
    )


def get_check_account_status_use_case(
    social_accounts_repository: Annotated[
        ISocialAccountsRepository, Depends(get_social_accounts_repository)
    ],
    credentials_protector: Annotated[
        ICredentialsProtector, Depends(get_credentials_protector)
    ],
) -> CheckSocialAccountStatusUseCase:
    """
    Generic factory for CheckSocialAccountStatusUseCase.

    Note: This returns the use case WITHOUT a validator.
    The validator will be injected at runtime based on the platform parameter.
    """
    return CheckSocialAccountStatusUseCase(
        social_accounts_repository=social_accounts_repository,
        credentials_protector=credentials_protector,
        validator=None,  # Will be set dynamically in endpoint
    )
