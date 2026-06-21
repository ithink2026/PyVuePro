"""H5 端登录接口（含 IP 登录、手机号注册/登录）"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.auth_service import (
    h5_login as h5_login_service,
    h5_ip_login,
    h5_send_sms_code,
    h5_register,
    h5_phone_login,
)

router = APIRouter(prefix="/auth/h5", tags=["H5端认证"])


@router.get("/login-mode")
async def get_login_mode():
    """H5 应用获取当前登录方式"""
    return {"mode": settings.H5_LOGIN_MODE}


@router.post("/login", response_model=TokenResponse)
async def h5_login(data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """H5 端用户名+密码登录（仅 h5_users 表）"""
    return await h5_login_service(db, data.username, data.password)


@router.post("/ip-login", response_model=TokenResponse)
async def h5_ip_login_api(request: Request, db: AsyncSession = Depends(get_db)):
    """H5 IP 自动登录"""
    client_ip = request.client.host if request.client else "127.0.0.1"
    return await h5_ip_login(db, client_ip)


@router.post("/send-code")
async def send_verification_code(data: dict):
    """发送手机验证码（万能验证码 6666）"""
    return await h5_send_sms_code(data.get("phone", ""))


@router.post("/register")
async def phone_register(data: dict, db: AsyncSession = Depends(get_db)):
    """手机号注册"""
    return await h5_register(
        db,
        phone=data.get("phone", ""),
        code=data.get("code", ""),
        password=data.get("password", ""),
        confirm_password=data.get("confirm_password", ""),
    )


@router.post("/phone-login", response_model=TokenResponse)
async def phone_login_api(data: dict, db: AsyncSession = Depends(get_db)):
    """手机号登录（支持验证码 或 密码）"""
    return await h5_phone_login(
        db,
        phone=data.get("phone", ""),
        code=data.get("code"),
        password=data.get("password"),
    )
