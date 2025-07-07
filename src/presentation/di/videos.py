from src.domain.use_cases.videos.generate_video import GenerateVideoUseCase

from src.domain.interfaces.repositories.user_repository import IUserRepository
from src.domain.interfaces.repositories.video_repository import IVideoRepository
from src.domain.interfaces.services.video_processor import IVideoProcessor

from src.presentation.di.repositories import get_user_repository, get_video_repository
from src.presentation.di.services import get_video_processor

from fastapi import Depends

from typing import Annotated


async def get_generate_video_use_case(
        user_repository: Annotated[IUserRepository, Depends(get_user_repository)],
        video_repository: Annotated[IVideoRepository, Depends(get_video_repository)],
        video_processor: Annotated[IVideoProcessor, Depends(get_video_processor)]
    ) -> GenerateVideoUseCase:
    return GenerateVideoUseCase(
        user_repository=user_repository,
        video_repository=video_repository,
        video_processor=video_processor
    )
