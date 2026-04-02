from unittest.mock import AsyncMock, MagicMock

import pytest

from src.domain.use_cases.videos.generate_video import GenerateVideoUseCase


@pytest.fixture
def mock_user_repository():
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_video_repository():
    repo = MagicMock()
    repo.get_video_format_by_id = AsyncMock()
    repo.create_video_job = AsyncMock()
    return repo


@pytest.fixture
def mock_balance_ledger_repository():
    repo = MagicMock()
    repo.create_transaction = AsyncMock()
    repo.has_transaction = AsyncMock(return_value=False)
    return repo


@pytest.fixture
def mock_video_processor():
    processor = MagicMock()
    return processor


@pytest.fixture
def generate_video_use_case(
    mock_user_repository,
    mock_video_repository,
    mock_balance_ledger_repository,
    mock_video_processor,
):
    return GenerateVideoUseCase(
        user_repository=mock_user_repository,
        video_repository=mock_video_repository,
        balance_ledger_repository=mock_balance_ledger_repository,
        video_processor=mock_video_processor,
    )
