from redis.asyncio import Redis

from .settings import get_settings


class YouTubeOAuthStateRepository:
    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.expiration_seconds = get_settings().STATE_TTL_SECONDS

    async def save_state(self, user_id: str, state: str) -> None:
        await self.redis_client.set(
            f"youtube_oauth_state:{user_id}", state, ex=self.expiration_seconds
        )

    async def get_state(self, user_id: str) -> str | None:
        state = await self.redis_client.get(f"youtube_oauth_state:{user_id}")
        return str(state, "utf-8") if state else None

    async def delete_state(self, user_id: str) -> None:
        await self.redis_client.delete(f"youtube_oauth_state:{user_id}")
