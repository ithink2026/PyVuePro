"""Redis 连接管理"""

import redis.asyncio as aioredis
from redis.asyncio import Redis

from app.core.config import settings

redis_client: Redis | None = None


async def init_redis() -> Redis:
    global redis_client
    redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis_client.ping()
    return redis_client


async def close_redis():
    global redis_client
    if redis_client:
        await redis_client.close()
        redis_client = None


def get_redis() -> Redis:
    """获取 Redis 客户端实例（必须在 init_redis 之后调用）"""
    if redis_client is None:
        raise RuntimeError("Redis 未初始化，请先调用 init_redis()")
    return redis_client