from .settings import settings

import redis.asyncio as redis


pool: redis.ConnectionPool = None
redis_client: redis.Redis = None


def init_redis():
    global redis_client, pool
    if redis_client is None:
        pool = redis.ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
        redis_client = redis.Redis.from_pool(pool)


async def close_redis():
    global redis_client, pool
    if redis_client is not None:
        await redis_client.close()
        pool = None
        redis_client = None


def get_redis_client() -> redis.Redis:
    global redis_client
    if redis_client is None:
        init_redis()
    return redis_client
