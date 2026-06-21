"""认证通用接口（Token 刷新、WebSocket 配置查询）"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import RefreshRequest, TokenResponse, WebSocketConfigResponse
from app.services.auth_service import refresh_access_token

router = APIRouter(prefix="/auth", tags=["认证"])


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(data: RefreshRequest, db: AsyncSession = Depends(get_db)):
    """刷新 Token"""
    return await refresh_access_token(data.refresh_token)


@router.get("/config/websocket-enabled", response_model=WebSocketConfigResponse)
async def get_websocket_config():
    """查询 WebSocket 长连接功能是否启用"""
    from app.core.config import settings

    return WebSocketConfigResponse(enabled=settings.ENABLE_WEBSOCKET)