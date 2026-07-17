"""Содержит компоненты модуля redis."""

from redis.asyncio import Redis

from app.core.config import settings

redis_client = Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD,
    decode_responses=True,
)


async def get_redis() -> Redis[str]:
    """Возвращает redis."""
    return redis_client
