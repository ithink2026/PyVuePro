"""管理端登录接口"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import admin_login as admin_login_service

router = APIRouter(prefix="/auth/admin", tags=["管理端认证"])


@router.post("/login", response_model=TokenResponse)
async def admin_login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """管理端登录（仅 users 表用户可登录）"""
    return await admin_login_service(db, data.username, data.password)