import redis.asyncio as aioredis
from app.core.config import settings

# This is our global Redis client.
# It gets created once when the app starts and reused for every request.
redis_client: aioredis.Redis | None = None


async def connect_redis():
    """
    Opens the connection to Redis.
    Called once when FastAPI starts up.
    """
    global redis_client
    redis_client = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,  # So we get plain strings back, not bytes
    )


async def disconnect_redis():
    """
    Closes the Redis connection.
    Called once when FastAPI shuts down.
    """
    global redis_client
    if redis_client:
        await redis_client.aclose()


def get_redis() -> aioredis.Redis:
    """
    Returns the active Redis client.
    Used as a FastAPI dependency in routes/services.
    """
    return redis_client
