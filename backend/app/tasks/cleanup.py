"""定时清理过期心跳"""

import asyncio

from app.core.config import settings
from app.services.online_service import cleanup_expired
from app.api.ws.admin import broadcast_online_count


async def heartbeat_cleanup_task():
    """后台任务：每 HEARTBEAT_CLEANUP_INTERVAL 秒扫描并清理过期心跳"""
    while True:
        await asyncio.sleep(settings.HEARTBEAT_CLEANUP_INTERVAL)
        try:
            cleaned = await cleanup_expired()
            if cleaned > 0:
                print(f"[cleanup] 清理了 {cleaned} 个过期心跳")
                # 异步通知（不阻塞清理循环）
                try:
                    asyncio.create_task(broadcast_online_count())
                except Exception:
                    pass
        except Exception as e:
            print(f"[cleanup] 清理任务异常: {e}")