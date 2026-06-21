"""管理端 WebSocket 端点（实时推送在线人数）"""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import verify_token
from app.services.online_service import get_online_count

router = APIRouter()

# 管理端连接池
admin_connections: list[WebSocket] = []


@router.websocket("/ws/admin")
async def admin_websocket(websocket: WebSocket):
    await websocket.accept()

    try:
        # 10 秒认证超时
        msg = await asyncio.wait_for(websocket.receive_json(), timeout=10)
        token = msg.get("token", "")
        payload = verify_token(token)

        if payload.get("port") != "admin":
            await websocket.close(code=4003, reason="无权访问此端点")
            return

        admin_connections.append(websocket)

        # 发送当前在线人数
        try:
            count = await get_online_count()
            await websocket.send_json({"type": "online_count", "count": count})
        except Exception:
            pass

        while True:
            data = await asyncio.wait_for(websocket.receive_json(), timeout=90)
            if data.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except asyncio.TimeoutError:
        pass
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if websocket in admin_connections:
            admin_connections.remove(websocket)


async def broadcast_online_count():
    """向所有管理端连接广播在线人数（有超时保护）"""
    try:
        count = await asyncio.wait_for(get_online_count(), timeout=5)
    except Exception:
        return  # Redis 不可用，跳过

    disconnected = []
    for ws in admin_connections:
        try:
            await asyncio.wait_for(
                ws.send_json({"type": "online_count", "count": count}),
                timeout=3,
            )
        except Exception:
            disconnected.append(ws)

    for ws in disconnected:
        try:
            admin_connections.remove(ws)
        except ValueError:
            pass