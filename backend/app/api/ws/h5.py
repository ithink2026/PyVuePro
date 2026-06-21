"""H5 端 WebSocket 端点（心跳）"""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import verify_token
from app.services.online_service import record_heartbeat, remove_user
from app.api.ws.admin import broadcast_online_count

router = APIRouter()


def _safe_broadcast():
    """异步广播，不阻塞当前协程，异常不传播"""
    try:
        asyncio.create_task(broadcast_online_count())
    except Exception:
        pass


@router.websocket("/ws/h5")
async def h5_websocket(websocket: WebSocket):
    await websocket.accept()
    user_id = None

    try:
        # 10 秒认证超时
        msg = await asyncio.wait_for(websocket.receive_json(), timeout=10)
        token = msg.get("token", "")
        payload = verify_token(token)

        if payload.get("port") != "h5":
            await websocket.close(code=4003, reason="无权访问此端点")
            return

        user_id = str(payload["user_id"])
        await record_heartbeat(user_id)
        # 异步通知管理端（不阻塞）
        _safe_broadcast()

        while True:
            data = await asyncio.wait_for(websocket.receive_json(), timeout=90)
            if data.get("type") == "ping":
                await record_heartbeat(user_id)
                await websocket.send_json({"type": "pong"})

    except asyncio.TimeoutError:
        pass
    except WebSocketDisconnect:
        pass
    except Exception:
        pass
    finally:
        if user_id:
            try:
                await remove_user(user_id)
            except Exception:
                pass
            # 异步通知管理端
            _safe_broadcast()