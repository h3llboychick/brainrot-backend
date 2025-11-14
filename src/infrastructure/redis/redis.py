from .settings import settings

import redis.asyncio as redis


class RedisConnectionManager:
    def __init__(self):
        self.pool = redis.ConnectionPool(
            host=settings.REDIS_HOST, 
            port=settings.REDIS_PORT, 
            db=settings.REDIS_DB,
            password=settings.REDIS_PASSWORD,
        )
        
    def get_client(self):
        return redis.Redis(
            decode_responses=True,
            connection_pool=self.pool
        )
    
redis_connection_manager = RedisConnectionManager()
