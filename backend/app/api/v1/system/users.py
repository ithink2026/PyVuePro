"""用户管理 CRUD（管理端用户，仅 admin 鉴权，不可创建 H5 用户）"""

from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ConflictError, ForbiddenError
from app.core.security import get_current_admin, require_permission, hash_password
from app.models.user import User
from app.services.user_service import get_user_by_username

router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("")
async def list_users(
    username: str = "",
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:user:list")),
):
    """获取所有管理端用户（不包含超级管理员）"""
    stmt = select(User).where(User.is_super_admin == False)
    if username:
        stmt = stmt.where(User.username.contains(username))
    result = await db.execute(
        stmt.options(joinedload(User.department), joinedload(User.role_rel))
    )
    users = result.unique().scalars().all()
    return [
        {
            "id": u.id, "username": u.username,
            "dept_id": u.dept_id, "dept_name": u.department.name if u.department else None,
            "role_id": u.role_id, "role_name": u.role_rel.name if u.role_rel else None,
            "created_at": u.created_at, "updated_at": u.updated_at,
        }
        for u in users
    ]


@router.post("", status_code=201)
async def add_user(
    data: dict,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:user:add")),
):
    """创建管理端用户（仅允许创建管理端用户，禁止创建 H5 用户）"""
    existing = await get_user_by_username(db, data["username"])
    if existing:
        raise ConflictError("该用户名已被使用，请更换后重试")

    user = User(
        username=data["username"],
        password=hash_password(data["password"]),
        dept_id=data.get("dept_id"),
        role_id=data.get("role_id"),
        is_super_admin=data.get("is_super_admin", False),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username}


@router.put("/{user_id}")
async def edit_user(
    user_id: int,
    data: dict,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:user:edit")),
):
    """编辑管理端用户"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("该用户不存在或已被删除")

    for field in ("username", "dept_id", "role_id", "is_super_admin"):
        if field in data and data[field] is not None:
            setattr(user, field, data[field])
    if data.get("password"):
        user.password = hash_password(data["password"])

    await db.commit()
    return {"message": "更新成功"}


@router.post("/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:user:edit")),
):
    """重置用户密码为 username+123"""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("该用户不存在或已被删除")

    new_pwd = user.username + "123"
    user.password = hash_password(new_pwd)
    await db.commit()
    return {"message": f"密码已重置为 {new_pwd}"}


@router.delete("/{user_id}")
async def remove_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:user:del")),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise NotFoundError("该用户不存在或已被删除")
    await db.delete(user)
    await db.commit()
    return {"message": "删除成功"}