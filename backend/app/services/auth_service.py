"""认证业务逻辑"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthError, BadRequestError, ForbiddenError
from app.core.security import create_access_token, create_refresh_token, verify_password, hash_password, verify_token
from app.models.user import User
from app.models.h5_user import H5User
from app.schemas.auth import TokenResponse


async def admin_login(db: AsyncSession, username: str, password: str) -> TokenResponse:
    """管理端登录（仅查 users 表）"""
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        raise BadRequestError("用户名或密码错误，请检查后重试")

    access_token = create_access_token(user.id, user.username, "admin")
    refresh_token = create_refresh_token(user.id, user.username, "admin")

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def h5_login(db: AsyncSession, username: str, password: str) -> TokenResponse:
    """H5 端登录（仅查 h5_users 表）"""
    result = await db.execute(select(H5User).where(H5User.username == username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(password, user.password):
        raise BadRequestError("用户名或密码错误，请检查后重试")

    if not user.is_active:
        raise BadRequestError("该账户已被禁用，请联系管理员")

    access_token = create_access_token(user.id, user.username, "h5")
    refresh_token = create_refresh_token(user.id, user.username, "h5")

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


async def refresh_access_token(refresh_token_str: str) -> TokenResponse:
    """刷新 Token"""
    try:
        payload = verify_token(refresh_token_str)
    except Exception:
        raise AuthError("登录信息已过期，请重新登录")

    if payload.get("type") != "refresh":
        raise AuthError("登录信息已过期，请重新登录")

    access_token = create_access_token(payload["user_id"], payload["username"], payload["port"])
    refresh_token = create_refresh_token(payload["user_id"], payload["username"], payload["port"])

    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# ─── IP 登录 ───
async def h5_ip_login(db: AsyncSession, client_ip: str) -> TokenResponse:
    """H5 IP 自动登录：基于 IP 地址查找或创建用户"""
    username = f"ip_{client_ip}"
    result = await db.execute(select(H5User).where(H5User.username == username))
    user = result.scalar_one_or_none()

    if not user:
        user = H5User(
            username=username,
            password=hash_password("ip_auto"),
            name=f"IP用户",
            phone=client_ip,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    if not user.is_active:
        raise BadRequestError("该账户已被禁用，请联系管理员")

    access_token = create_access_token(user.id, user.username, "h5")
    refresh_token = create_refresh_token(user.id, user.username, "h5")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)


# ─── 手机号注册/登录 ───
# 万能验证码
MAGIC_CODE = "6666"


async def h5_send_sms_code(phone: str) -> dict:
    """发送短信验证码（万能验证码 6666）"""
    if not phone or len(phone) < 11:
        raise BadRequestError("请输入正确的手机号")
    return {"message": "验证码已发送（万能验证码: 6666）", "code": MAGIC_CODE}


async def h5_register(db: AsyncSession, phone: str, code: str, password: str, confirm_password: str) -> dict:
    """手机号注册"""
    if code != MAGIC_CODE:
        raise BadRequestError("验证码错误，请重新输入")

    if password != confirm_password:
        raise BadRequestError("两次输入的密码不一致")

    if len(password) < 6:
        raise BadRequestError("密码长度至少为6位")

    # 检查手机号是否已注册
    result = await db.execute(select(H5User).where(H5User.username == phone))
    if result.scalar_one_or_none():
        raise BadRequestError("该手机号已注册，请直接登录")

    user = H5User(
        username=phone,
        password=hash_password(password),
        name="",
        phone=phone,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(user.id, user.username, "h5")
    refresh_token = create_refresh_token(user.id, user.username, "h5")
    return {"message": "注册成功", "access_token": access_token, "refresh_token": refresh_token}


async def h5_phone_login(db: AsyncSession, phone: str, code: str | None = None, password: str | None = None) -> TokenResponse:
    """手机号登录：验证码登录（自动注册）或 密码登录"""
    result = await db.execute(select(H5User).where(H5User.username == phone))
    user = result.scalar_one_or_none()

    # 验证码登录
    if code:
        if code != MAGIC_CODE:
            raise BadRequestError("验证码错误，请重新输入")

        # 自动注册
        if not user:
            user = H5User(
                username=phone,
                password=hash_password(phone),  # 默认密码为手机号
                name="",
                phone=phone,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)

    # 密码登录
    elif password:
        if not user:
            raise BadRequestError("该手机号未注册，请先使用验证码登录完成注册")
        if not verify_password(password, user.password):
            raise BadRequestError("密码错误，请重新输入")
    else:
        raise BadRequestError("请提供验证码或密码")

    if not user.is_active:
        raise BadRequestError("该账户已被禁用，请联系管理员")

    access_token = create_access_token(user.id, user.username, "h5")
    refresh_token = create_refresh_token(user.id, user.username, "h5")
    return TokenResponse(access_token=access_token, refresh_token=refresh_token)