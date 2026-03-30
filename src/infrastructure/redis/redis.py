import redis.asyncio as aioredis

from .settings import get_settings


class RedisClient:
    def __init__(self):
        self._pool: aioredis.ConnectionPool | None = None
        self._client: aioredis.Redis | None = None

    @property
    def is_initialized(self) -> bool:
        return self._client is not None

    def init(self, settings=None):
        if self.is_initialized:
            return
        settings = settings or get_settings()
        self._pool = aioredis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
        self._client = aioredis.Redis.from_pool(self._pool)

    async def close(self):
        if self._client is not None:
            await self._client.close()
            self._pool = None
            self._client = None

    def get_client(self) -> aioredis.Redis:
        if not self.is_initialized:
            raise RuntimeError(
                "Redis is not initialized. Call RedisClient.init() first "
                "(this normally happens in the application lifespan)."
            )
        return self._client


redis_client = RedisClient()
