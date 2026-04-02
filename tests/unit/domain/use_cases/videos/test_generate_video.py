from datetime import datetime, timezone

import pytest

from src.domain.dtos.videos import VideoGenerationRequestDTO
from src.domain.entities import User, VideoFormat, VideoJob
from src.domain.enums import SocialPlatform, VideoJobStatus
from src.domain.exceptions import (
    InsufficientBalanceError,
    UserNotFoundError,
    VideoFormatNotFoundError,
)


# Scenario 1: user not found
@pytest.mark.asyncio
async def test_generate_video_user_not_found(
    generate_video_use_case, mock_user_repository
):
    mock_user_repository.get_by_id.return_value = None

    dto = VideoGenerationRequestDTO(
        user_id="user123",
        format_id=1,
        prompt="Create a funny video",
    )

    with pytest.raises(UserNotFoundError):
        await generate_video_use_case.execute(dto)

    mock_user_repository.get_by_id.assert_called_once_with(user_id="user123")


# Scenario 2: invalid video format
@pytest.mark.asyncio
async def test_generate_video_invalid_format(
    generate_video_use_case, mock_user_repository, mock_video_repository
):
    mock_user_repository.get_by_id.return_value = User(
        id="user123",
        email="user@test.com",
        is_active=True,
        is_verified=True,
        balance=100.0,
        created_at=datetime.now(timezone.utc),
    )
    mock_video_repository.get_video_format_by_id.return_value = None

    dto = VideoGenerationRequestDTO(
        user_id="user123",
        format_id=999,
        prompt="Create a funny video",
    )

    with pytest.raises(VideoFormatNotFoundError):
        await generate_video_use_case.execute(dto)

    mock_video_repository.get_video_format_by_id.assert_called_once_with(
        format_id=999
    )


# Scenario 3: insufficient balance
@pytest.mark.asyncio
async def test_generate_video_insufficient_balance(
    generate_video_use_case, mock_user_repository, mock_video_repository
):
    mock_user_repository.get_by_id.return_value = User(
        id="user123",
        email="user@test.com",
        is_active=True,
        is_verified=True,
        balance=5.0,
        created_at=datetime.now(timezone.utc),
    )
    mock_video_repository.get_video_format_by_id.return_value = VideoFormat(
        id=1,
        name="short",
        description="Short video",
        price=10.0,
    )

    dto = VideoGenerationRequestDTO(
        user_id="user123",
        format_id=1,
        prompt="Create a funny video",
    )

    with pytest.raises(InsufficientBalanceError):
        await generate_video_use_case.execute(dto)


# Scenario 4: successful video generation (reserves balance, doesn't deduct)
@pytest.mark.asyncio
async def test_generate_video_success(
    generate_video_use_case,
    mock_user_repository,
    mock_video_repository,
    mock_balance_ledger_repository,
    mock_video_processor,
):
    user = User(
        id="user123",
        email="user@test.com",
        is_active=True,
        is_verified=True,
        balance=100.0,
        created_at=datetime.now(timezone.utc),
    )
    mock_user_repository.get_by_id.return_value = user

    video_format = VideoFormat(
        id=1,
        name="short",
        description="Short video",
        price=10.0,
    )
    mock_video_repository.get_video_format_by_id.return_value = video_format

    created_job = VideoJob(
        id="job_123",
        creator_id="user123",
        format_id=1,
        status=VideoJobStatus.queued,
    )
    mock_video_repository.create_video_job.return_value = created_job

    dto = VideoGenerationRequestDTO(
        user_id="user123",
        format_id=1,
        prompt="Create a funny video",
        platform=SocialPlatform.youtube,
    )
    result = await generate_video_use_case.execute(dto)

    mock_user_repository.get_by_id.assert_called_once_with(user_id="user123")
    mock_video_repository.get_video_format_by_id.assert_called_once_with(
        format_id=1
    )
    mock_user_repository.update.assert_called_once_with(user)
    # Balance stays the same; funds are held in reserved_balance
    assert user.balance == 100.0
    assert user.reserved_balance == 10.0
    assert user.available_balance == 90.0
    mock_video_repository.create_video_job.assert_called_once()
    mock_balance_ledger_repository.create_transaction.assert_called_once()
    mock_video_processor.schedule_generation.assert_called_once()
    assert result.video_job_id == "job_123"


# Scenario 5: successful video generation without platform
@pytest.mark.asyncio
async def test_generate_video_success_no_platform(
    generate_video_use_case,
    mock_user_repository,
    mock_video_repository,
    mock_balance_ledger_repository,
    mock_video_processor,
):
    user = User(
        id="user123",
        email="user@test.com",
        is_active=True,
        is_verified=True,
        balance=50.0,
        created_at=datetime.now(timezone.utc),
    )
    mock_user_repository.get_by_id.return_value = user

    video_format = VideoFormat(
        id=2,
        name="long",
        description="Long video",
        price=20.0,
    )
    mock_video_repository.get_video_format_by_id.return_value = video_format

    created_job = VideoJob(
        id="job_456",
        creator_id="user123",
        format_id=2,
        status=VideoJobStatus.queued,
    )
    mock_video_repository.create_video_job.return_value = created_job

    dto = VideoGenerationRequestDTO(
        user_id="user123",
        format_id=2,
        prompt="Create another video",
    )
    result = await generate_video_use_case.execute(dto)

    # Balance stays the same; funds are held in reserved_balance
    assert user.balance == 50.0
    assert user.reserved_balance == 20.0
    assert user.available_balance == 30.0
    assert result.video_job_id == "job_456"
    mock_balance_ledger_repository.create_transaction.assert_called_once()
    mock_video_processor.schedule_generation.assert_called_once()


# Scenario 6: insufficient available balance due to existing reservation
@pytest.mark.asyncio
async def test_generate_video_insufficient_available_balance(
    generate_video_use_case,
    mock_user_repository,
    mock_video_repository,
):
    user = User(
        id="user123",
        email="user@test.com",
        is_active=True,
        is_verified=True,
        balance=20.0,
        reserved_balance=15.0,  # only 5.0 available
        created_at=datetime.now(timezone.utc),
    )
    mock_user_repository.get_by_id.return_value = user

    mock_video_repository.get_video_format_by_id.return_value = VideoFormat(
        id=1,
        name="short",
        description="Short video",
        price=10.0,
    )

    dto = VideoGenerationRequestDTO(
        user_id="user123",
        format_id=1,
        prompt="Create a funny video",
    )

    with pytest.raises(InsufficientBalanceError):
        await generate_video_use_case.execute(dto)
