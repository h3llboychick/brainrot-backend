from ..settings import settings

import redis


pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    password=settings.REDIS_PASSWORD,
)


def get_redis_client() -> redis.Redis:
    return redis.Redis(connection_pool=pool)
