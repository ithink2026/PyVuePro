"""角色管理 API"""

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.core.security import get_current_admin, require_permission
from app.models.role import Role
from app.schemas.rbac import RoleCreate, RoleUpdate
from app.services.rbac_service import (
    get_role_list, create_role, update_role, delete_role,
)

router = APIRouter(prefix="/roles", tags=["角色管理"])


@router.get("")
async def list_roles(
    name: str = "",
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:role:list")),
):
    return await get_role_list(db, name)


@router.post("", status_code=201)
async def add_role(
    data: RoleCreate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:role:add")),
):
    return await create_role(db, data.model_dump())


@router.put("/{role_id}")
async def edit_role(
    role_id: int,
    data: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(require_permission("system:role:edit")),
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise NotFoundError("角色不存在或已被删除")
    if role.is_system and not admin.get("is_super_admin"):
        raise ForbiddenError("系统角色仅超级管理员可编辑，如需修改请联系管理员")
    role = await update_role(db, role_id, data.model_dump(exclude_none=True))
    return role


@router.delete("/{role_id}")
async def remove_role(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:role:del")),
):
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        raise NotFoundError("角色不存在或已被删除")
    if role.is_system:
        raise ForbiddenError("系统角色不可删除，如需调整请联系管理员")
    if not await delete_role(db, role_id):
        raise NotFoundError("角色不存在或已被删除")
    return {"message": "删除成功"}