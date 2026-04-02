import asyncio
import json
from typing import Annotated

from fastapi import APIRouter, Depends, Request, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from src.domain.dtos.videos import VideoGenerationRequestDTO
from src.domain.use_cases.videos.generate_video import GenerateVideoUseCase
from src.domain.use_cases.videos.list_video_formats import (
    ListVideoFormatsUseCase,
)
from src.infrastructure.rate_limiting import limiter
from src.infrastructure.redis import redis_client
from src.presentation.di.auth import get_current_user_id
from src.presentation.di.videos import (
    get_generate_video_use_case,
    get_list_video_formats_use_case,
)
from src.presentation.schemas import (
    ListVideoFormatsResponse,
    VideoFormatResponse,
    VideoGenerationRequest,
    VideoGenerationResponse,
)

router = APIRouter(prefix="/videos", tags=["Video Geneartion"])


@router.get(
    "/formats",
    description="List all available video formats with their prices.",
    response_model=ListVideoFormatsResponse,
    status_code=200,
)
async def list_video_formats(
    use_case: Annotated[
        ListVideoFormatsUseCase, Depends(get_list_video_formats_use_case)
    ],
) -> ListVideoFormatsResponse:
    formats = await use_case.execute()
    return ListVideoFormatsResponse(
        formats=[
            VideoFormatResponse(
                id=f.id,
                name=f.name,
                description=f.description,
                price=f.price,
            )
            for f in formats
        ],
        total_count=len(formats),
    )


@router.post(
    "/generate",
    description="Generate a video based on the provided prompt and format. Optionally specify a social platform for publishing.",
    response_model=VideoGenerationResponse,
    status_code=200,
)
@limiter.limit("5/minute")
async def generate_video(
    user_id: Annotated[str, Depends(get_current_user_id)],
    video_data: VideoGenerationRequest,
    use_case: Annotated[
        GenerateVideoUseCase, Depends(get_generate_video_use_case)
    ],
    request: Request,
) -> VideoGenerationResponse:
    result = await use_case.execute(
        dto=VideoGenerationRequestDTO(
            user_id=user_id,
            prompt=video_data.prompt,
            format_id=video_data.format_id,
            platform=video_data.platform,
        )
    )

    return VideoGenerationResponse(video_job_id=result.video_job_id)


@router.websocket("/ws/{video_job_id}")
async def video_websocket(
    websocket: WebSocket,
    redis_session: Annotated[Redis, Depends(redis_client.get_client)],
    video_job_id: str,
):
    await websocket.accept()

    channel = f"video_job:{video_job_id}"
    pubsub = redis_session.pubsub()

    await pubsub.subscribe(channel)

    async def forward_pubsub_to_ws():
        async for msg in pubsub.listen():
            try:
                payload = json.loads(msg)
                await websocket.send_json(payload)
            except Exception:
                await websocket.send_text(str(msg))

    forward_task = asyncio.create_task(forward_pubsub_to_ws())

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        forward_task.cancel()
    finally:
        await pubsub.unsubscribe(channel)
        await pubsub.close()
        await websocket.close()
