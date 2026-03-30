from typing import Annotated

from fastapi import APIRouter, Depends

from src.presentation.di.auth import get_current_user_id
from src.presentation.schemas import UserMeInformationResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    description="Get information about the authenticated user.",
    response_model=UserMeInformationResponse,
    status_code=200,
)
async def get_me(user_id: Annotated[str, Depends(get_current_user_id)]):
    return UserMeInformationResponse(user_id=user_id)
