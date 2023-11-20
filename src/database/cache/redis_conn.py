import redis.asyncio as redis

from src.config import settings


class Redis:
    def __init__(self):
        self.redis_url = f"redis://{settings.redis_host}:{settings.redis_port}"
        self.redis = None
        print("REDIS_CONNECTOR_INITIALIZED")

    async def __call__(self):
        if self.redis is None:
            self.redis = await redis.from_url(self.redis_url)
        return self.redis


cache_database = Redis()
