from __future__ import annotations

from functools import lru_cache

from redis.asyncio import Redis

from config import settings


@lru_cache(maxsize=1)
def get_redis() -> Redis:
    return Redis.from_url(settings.redis_url, decode_responses=True)


async def close_redis() -> None:
    await get_redis().aclose()
