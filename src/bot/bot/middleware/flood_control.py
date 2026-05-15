from __future__ import annotations

import time

from src.bot.bot.middleware.rate_limiter import get_redis

FLOOD_KEY = "flood:{chat_id}:{user_id}"
RAID_KEY = "raid:{chat_id}"
FLOOD_WINDOW_SECONDS = 5
RAID_WINDOW_SECONDS = 30
RAID_THRESHOLD = 10


async def check_flood(
    chat_id: int,
    user_id: int,
    limit: int,
    window_seconds: int = FLOOD_WINDOW_SECONDS,
) -> bool:
    if limit <= 0:
        return False
    redis = get_redis()
    key = FLOOD_KEY.format(chat_id=chat_id, user_id=user_id)
    now = time.time()
    member = f"{now}:{time.time_ns()}"
    pipe = redis.pipeline()
    pipe.zadd(key, {member: now})
    pipe.zremrangebyscore(key, 0, now - window_seconds)
    pipe.zcard(key)
    pipe.expire(key, window_seconds * 2)
    _, _, count, _ = await pipe.execute()
    return int(count) > limit


async def count_recent_join(chat_id: int) -> int:
    redis = get_redis()
    key = RAID_KEY.format(chat_id=chat_id)
    count = await redis.incr(key)
    await redis.expire(key, RAID_WINDOW_SECONDS)
    return int(count)


async def raid_threshold_reached(chat_id: int) -> bool:
    return await count_recent_join(chat_id) >= RAID_THRESHOLD
