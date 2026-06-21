"""JWT 生成/校验、密码哈希、RBAC 权限守卫"""

import json
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from fastapi import Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import AuthError, ForbiddenError, AppError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, username: str, port: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "username": username,
        "port": port,
        "type": "access",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(user_id: int, username: str, port: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "user_id": user_id,
        "username": username,
        "port": port,
        "type": "refresh",
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_token(token: str) -> dict:
    """校验 Token 并返回 payload，校验失败抛出 AuthError"""
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise AuthError("登录信息已过期，请重新登录")
    except jwt.InvalidTokenError:
        raise AuthError("登录信息无效，请重新登录")


# ─── 管理端用户信息 Payload ───
async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    request: Request = None,
) -> dict:
    """依赖：校验 admin JWT，返回 payload（含 user_id, username, port, is_super_admin, role_id）"""
    payload = verify_token(credentials.credentials)
    if payload.get("type") != "access":
        raise AuthError("登录信息已过期，请重新登录")
    if payload.get("port") != "admin":
        raise ForbiddenError("仅管理员可访问此功能")

    # 查询 is_super_admin 和 role_id
    try:
        from app.core.database import async_session_factory
        from app.models.user import User

        async with async_session_factory() as db:
            result = await db.execute(select(User).where(User.id == payload["user_id"]))
            user = result.scalar_one_or_none()
            if user:
                payload["is_super_admin"] = user.is_super_admin
                payload["role_id"] = user.role_id
    except Exception:
        payload["is_super_admin"] = False
        payload["role_id"] = None

    return payload


# ─── Super Admin 信息查询依赖 ───
async def get_admin_info(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """依赖：获取 admin 完整信息（供前端/user_info接口用）"""
    payload = await get_current_admin(credentials)
    return payload


# ─── 按钮级权限检查 ───
def require_permission(permission: str):
    """工厂函数：返回一个 FastAPI 依赖，检查按钮级权限"""
    async def _check(credentials: HTTPAuthorizationCredentials = Depends(security)):
        payload = await get_current_admin(credentials)
        # 超级管理员跳过所有权限检查
        if payload.get("is_super_admin"):
            return payload

        role_id = payload.get("role_id")
        if role_id is None:
            raise ForbiddenError("您没有分配角色，无法执行此操作")

        try:
            from app.services.rbac_service import get_user_permissions
            from app.core.database import async_session_factory

            async with async_session_factory() as db:
                perms = await get_user_permissions(db, role_id)
                if permission not in perms:
                    raise ForbiddenError("您没有执行此操作的权限，请联系管理员")
        except AppError:
            raise
        except Exception:
            raise ForbiddenError("权限校验失败，请稍后重试")

        return payload
    return _check
