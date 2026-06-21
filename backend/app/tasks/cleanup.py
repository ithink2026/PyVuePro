"""定时清理过期心跳"""

import asyncio

from app.core.config import settings
from app.services.online_service import cleanup_expired


async def heartbeat_cleanup_task():
    """后台任务：每 HEARTBEAT_CLEANUP_INTERVAL 秒扫描并清理过期心跳"""
    while True:
        await asyncio.sleep(settings.HEARTBEAT_CLEANUP_INTERVAL)
        try:
            cleaned = await cleanup_expired()
            if cleaned > 0:
                print(f"[cleanup] 清理了 {cleaned} 个过期心跳")
        except Exception as e:
            print(f"[cleanup] 清理任务异常: {e}")