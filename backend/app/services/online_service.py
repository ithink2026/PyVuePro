"""在线人数统计服务"""

import time

from app.core.config import settings
from app.utils.redis import get_redis

ONLINE_USERS_KEY = "online_users"


async def record_heartbeat(user_id: str) -> None:
    """记录用户心跳"""
    if not settings.ENABLE_WEBSOCKET:
        return
    redis = get_redis()
    await redis.hset(ONLINE_USERS_KEY, user_id, time.time())


async def remove_user(user_id: str) -> None:
    """移除用户在线状态"""
    redis = get_redis()
    await redis.hdel(ONLINE_USERS_KEY, user_id)


async def get_online_users() -> list[dict]:
    """获取所有在线用户及心跳时间"""
    redis = get_redis()
    data = await redis.hgetall(ONLINE_USERS_KEY)
    return [{"user_id": k, "heartbeat": float(v)} for k, v in data.items()]


async def cleanup_expired() -> int:
    """清理过期心跳（超过 HEARTBEAT_TIMEOUT 秒无心跳），返回清理数量"""
    redis = get_redis()
    now = time.time()
    data = await redis.hgetall(ONLINE_USERS_KEY)

    expired = [uid for uid, ts in data.items() if now - float(ts) > settings.HEARTBEAT_TIMEOUT]
    if expired:
        await redis.hdel(ONLINE_USERS_KEY, *expired)
    return len(expired)