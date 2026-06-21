"""H5 用户管理 CRUD（独立 h5_users 表，含敏感个人信息字段，需 admin 鉴权）"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ConflictError
from app.core.security import get_current_admin, require_permission, hash_password
from app.models.h5_user import H5User

router = APIRouter(prefix="/h5-users", tags=["客户管理"])


@router.get("")
async def list_h5_users(
    username: str = "",
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("h5:user:list")),
):
    """获取所有 H5 用户（仅 h5_users 表）"""
    stmt = select(H5User)
    if username:
        stmt = stmt.where(H5User.username.contains(username))
    result = await db.execute(stmt)
    users = result.scalars().all()
    return [
        {
            "id": u.id, "username": u.username,
            "is_active": u.is_active,
            "name": u.name, "id_card": u.id_card, "phone": u.phone,
            "bank_card": u.bank_card, "bank_card_name": u.bank_card_name,
            "bank_card_balance": float(u.bank_card_balance) if u.bank_card_balance is not None else None,
            "created_at": u.created_at, "updated_at": u.updated_at,
        }
        for u in users
    ]


@router.post("", status_code=201)
async def add_h5_user(
    data: dict,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("h5:user:add")),
):
    """创建 H5 用户（写入 h5_users 表，含敏感个人信息）"""
    result = await db.execute(select(H5User).where(H5User.username == data["username"]))
    if result.scalar_one_or_none():
        raise ConflictError("该用户名已被使用，请更换后重试")

    user = H5User(
        username=data["username"],
        password=hash_password(data["password"]),
        name=data.get("name"),
        id_card=data.get("id_card"),
        phone=data.get("phone"),
        bank_card=data.get("bank_card"),
        bank_card_name=data.get("bank_card_name"),
        bank_card_balance=data.get("bank_card_balance"),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username}


@router.put("/{user_id}")
async def edit_h5_user(
    user_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("h5:user:edit")),
):
    """编辑 H5 用户"""
    result = await db.execute(select(H5User).where(H5User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("该 H5 用户不存在或已被删除")

    for field in ("username", "name", "id_card", "phone", "bank_card", "bank_card_name", "bank_card_balance"):
        if field in data and data[field] is not None:
            setattr(user, field, data[field])
    if data.get("password"):
        user.password = hash_password(data["password"])

    await db.commit()
    return {"message": "更新成功"}


@router.post("/{user_id}/reset-password")
async def reset_h5_user_password(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("h5:user:edit")),
):
    """重置 H5 用户密码为 username+123"""
    result = await db.execute(select(H5User).where(H5User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("该 H5 用户不存在或已被删除")

    new_pwd = user.username + "123"
    user.password = hash_password(new_pwd)
    await db.commit()
    return {"message": f"密码已重置为 {new_pwd}"}


@router.delete("/{user_id}")
async def remove_h5_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("h5:user:del")),
):
    """删除 H5 用户"""
    result = await db.execute(select(H5User).where(H5User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("该 H5 用户不存在或已被删除")
    await db.delete(user)
    await db.commit()
    return {"message": "删除成功"}


@router.put("/{user_id}/toggle-status")
async def toggle_h5_user_status(
    user_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("h5:user:edit")),
):
    """切换 H5 用户启用/禁用状态"""
    result = await db.execute(select(H5User).where(H5User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("该 H5 用户不存在或已被删除")

    user.is_active = data.get("is_active", not user.is_active)
    await db.commit()
    return {"is_active": user.is_active, "message": "已启用" if user.is_active else "已禁用"}