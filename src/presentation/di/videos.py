from typing import Annotated

from fastapi import Depends

from src.domain.interfaces.repositories import (
    IBalanceLedgerRepository,
    IUserRepository,
    IVideoRepository,
)
from src.domain.interfaces.services import IVideoProcessor
from src.domain.use_cases.videos.generate_video import GenerateVideoUseCase
from src.domain.use_cases.videos.list_video_formats import (
    ListVideoFormatsUseCase,
)
from src.presentation.di.repositories import (
    get_balance_ledger_repository,
    get_user_repository,
    get_video_repository,
)
from src.presentation.di.services import get_video_processor


async def get_list_video_formats_use_case(
    video_repository: Annotated[
        IVideoRepository, Depends(get_video_repository)
    ],
) -> ListVideoFormatsUseCase:
    return ListVideoFormatsUseCase(video_repository=video_repository)


async def get_generate_video_use_case(
    user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
    video_repository: Annotated[
        IVideoRepository, Depends(get_video_repository)
    ],
    balance_ledger_repository: Annotated[
        IBalanceLedgerRepository, Depends(get_balance_ledger_repository)
    ],
    video_processor: Annotated[IVideoProcessor, Depends(get_video_processor)],
) -> GenerateVideoUseCase:
    return GenerateVideoUseCase(
        user_repository=user_repository,
        video_repository=video_repository,
        balance_ledger_repository=balance_ledger_repository,
        video_processor=video_processor,
    )
