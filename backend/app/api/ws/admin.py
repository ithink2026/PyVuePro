"""管理端 WebSocket 端点"""

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.core.security import verify_token

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