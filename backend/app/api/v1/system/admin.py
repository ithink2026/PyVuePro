"""管理端通用接口（用户信息、修改密码、WebSocket开关）"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from app.core.config import settings
from app.core.exceptions import BadRequestError, ForbiddenError
from app.core.security import get_admin_info, hash_password, verify_password
from app.schemas.rbac import WebSocketToggleRequest, WebSocketToggleResponse
from app.models.user import User
from app.models.h5_user import H5User
from app.core.database import async_session_factory

router = APIRouter(prefix="/admin", tags=["管理端通用"])


@router.get("/info")
async def admin_info(admin: dict = Depends(get_admin_info)):
    """当前登录用户信息"""
    role_name = None
    if admin.get("role_id"):
        try:
            from app.models.role import Role
            async with async_session_factory() as db:
                result = await db.execute(select(Role).where(Role.id == admin["role_id"]))
                role = result.scalar_one_or_none()
                role_name = role.name if role else None
        except Exception:
            pass

    return {
        "username": admin["username"],
        "user_id": admin["user_id"],
        "is_super_admin": admin.get("is_super_admin", False),
        "role_id": admin.get("role_id"),
        "role_name": role_name,
    }


@router.post("/change-password")
async def change_password(data: dict, admin: dict = Depends(get_admin_info)):
    """修改当前用户密码"""
    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")
    if not old_password or not new_password:
        raise BadRequestError("请填写旧密码和新密码")
    if len(new_password) < 6:
        raise BadRequestError("新密码至少需要6位，请重新设置")

    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.id == admin["user_id"]))
        user = result.scalar_one_or_none()
        if not user or not verify_password(old_password, user.password):
            raise BadRequestError("当前密码不正确，请重新输入")
        user.password = hash_password(new_password)
        await db.commit()
    return {"message": "密码修改成功，下次登录时请使用新密码"}


@router.get("/ws-config", response_model=WebSocketToggleResponse)
async def get_ws_config(admin: dict = Depends(get_admin_info)):
    return WebSocketToggleResponse(enabled=settings.ENABLE_WEBSOCKET)


@router.post("/ws-toggle", response_model=WebSocketToggleResponse)
async def toggle_ws(data: WebSocketToggleRequest, admin: dict = Depends(get_admin_info)):
    if not admin.get("is_super_admin"):
        raise ForbiddenError("WebSocket 开关仅超级管理员可操作")
    # H5 未启用时不允许开启 WebSocket
    if data.enabled and not settings.H5_ENABLED:
        raise BadRequestError("H5 端未启用，请先在功能控制中开启「H5 是否存在」后再开启 WebSocket")
    settings.ENABLE_WEBSOCKET = data.enabled
    return WebSocketToggleResponse(enabled=settings.ENABLE_WEBSOCKET)


@router.get("/h5-config")
async def get_h5_config(admin: dict = Depends(get_admin_info)):
    """获取 H5 是否存在开关状态"""
    return {"enabled": settings.H5_ENABLED}


@router.post("/h5-config")
async def toggle_h5(data: dict, admin: dict = Depends(get_admin_info)):
    """切换 H5 是否存在开关，关闭时自动关闭 WebSocket"""
    if not admin.get("is_super_admin"):
        raise ForbiddenError("该功能仅超级管理员可操作")
    enabled = data.get("enabled", True)
    settings.H5_ENABLED = enabled
    if not enabled:
        settings.ENABLE_WEBSOCKET = False
    return {"enabled": settings.H5_ENABLED, "ws_enabled": settings.ENABLE_WEBSOCKET}


@router.get("/h5-status")
async def get_h5_status(admin: dict = Depends(get_admin_info)):
    """检测 H5 端是否存在（H5 已启用、有 H5 用户 且 WebSocket 已开启）"""
    has_users = False
    try:
        async with async_session_factory() as db:
            result = await db.execute(select(H5User).limit(1))
            has_users = result.scalar_one_or_none() is not None
    except Exception:
        pass
    return {
        "h5_enabled": settings.H5_ENABLED,
        "h5_ready": settings.H5_ENABLED and has_users and settings.ENABLE_WEBSOCKET,
        "ws_enabled": settings.ENABLE_WEBSOCKET,
        "has_h5_users": has_users,
    }


@router.get("/h5-login-config")
async def get_h5_login_config(admin: dict = Depends(get_admin_info)):
    """获取 H5 登录方式配置"""
    return {"mode": settings.H5_LOGIN_MODE}


@router.post("/h5-login-config")
async def toggle_h5_login_mode(data: dict, admin: dict = Depends(get_admin_info)):
    """切换 H5 登录方式: ip / phone"""
    if not admin.get("is_super_admin"):
        raise ForbiddenError("该功能仅超级管理员可操作")
    mode = data.get("mode", "phone")
    if mode not in ("ip", "phone"):
        raise BadRequestError("无效的登录方式，仅支持 ip 或 phone")
    settings.H5_LOGIN_MODE = mode
    return {"mode": settings.H5_LOGIN_MODE}