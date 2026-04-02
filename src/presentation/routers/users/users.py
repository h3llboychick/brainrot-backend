from typing import Annotated

from fastapi import APIRouter, Depends

from src.domain.exceptions import UserNotFoundError
from src.domain.interfaces.repositories import IUserRepository
from src.presentation.di.auth import get_current_user_id
from src.presentation.di.repositories import get_user_repository
from src.presentation.schemas import (
    UserBalanceResponse,
    UserMeInformationResponse,
)

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    description="Get information about the authenticated user.",
    response_model=UserMeInformationResponse,
    status_code=200,
)
async def get_me(user_id: Annotated[str, Depends(get_current_user_id)]):
    return UserMeInformationResponse(user_id=user_id)


@router.get(
    "/me/balance",
    description="Get the authenticated user's balance details.",
    response_model=UserBalanceResponse,
    status_code=200,
)
async def get_my_balance(
    user_id: Annotated[str, Depends(get_current_user_id)],
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
):
    user = await user_repository.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError(user_id=user_id)
    return UserBalanceResponse(
        balance=user.balance,
        reserved_balance=user.reserved_balance,
        available_balance=user.available_balance,
    )
