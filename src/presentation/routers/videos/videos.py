from src.domain.use_cases.videos.generate_video import GenerateVideoUseCase
from src.domain.dtos.videos import VideoGenerationRequestDTO

from src.infrastructure.redis import get_redis_client

from src.presentation.schemas import VideoGenerationRequest, VideoGenerationResponse
from src.presentation.di.auth import get_current_user_id
from src.presentation.di.videos import get_generate_video_use_case

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from typing import Annotated
import json
import asyncio


router = APIRouter(prefix="/videos", tags=["videos"])


@router.post("/generate")
async def generate_video(
    user_id: Annotated[str, Depends(get_current_user_id)],
    video_data: VideoGenerationRequest,
    use_case: Annotated[GenerateVideoUseCase, Depends(get_generate_video_use_case)],
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
    redis_session: Annotated[Redis, Depends(get_redis_client)],
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
