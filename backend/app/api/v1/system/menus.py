"""菜单管理 API"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import NotFoundError
from app.core.config import settings
from app.core.security import get_current_admin, require_permission
from app.schemas.rbac import MenuCreate, MenuUpdate
from app.services.rbac_service import (
    get_menu_tree, get_sidebar_menu_tree, get_menu_flat_list, create_menu, update_menu,
    delete_menu, get_user_menus_for_sidebar, get_assignable_menu_tree,
)

router = APIRouter(prefix="/menus", tags=["菜单管理"])


@router.get("/tree")
async def list_menu_tree(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:menu:list")),
):
    return await get_menu_tree(db)


@router.get("/flat")
async def list_menus_flat(
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:menu:list")),
):
    return await get_menu_flat_list(db)


@router.get("/sidebar")
async def get_sidebar_menus(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """当前用户可见的侧边栏菜单（不包含按钮类型子项）"""
    if admin.get("is_super_admin"):
        menus = await get_sidebar_menu_tree(db)
    else:
        menus = await get_user_menus_for_sidebar(db, admin.get("role_id"))
    # H5 未启用时隐藏客户管理菜单
    if not settings.H5_ENABLED:
        menus = [m for m in menus if m.get("id") != 20]
    return menus


@router.get("/assignable")
async def get_assignable_menus(
    db: AsyncSession = Depends(get_db),
    admin: dict = Depends(get_current_admin),
):
    """当前用户可分配给他人的菜单树（超管看全部，普通用户只看自己拥有的）"""
    if admin.get("is_super_admin"):
        return await get_menu_tree(db)
    return await get_assignable_menu_tree(db, admin.get("role_id"))


@router.post("", status_code=201)
async def add_menu(
    data: MenuCreate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:menu:add")),
):
    return await create_menu(db, data.model_dump())


@router.put("/{menu_id}")
async def edit_menu(
    menu_id: int,
    data: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:menu:edit")),
):
    menu = await update_menu(db, menu_id, data.model_dump(exclude_none=True))
    if not menu:
        raise NotFoundError("菜单不存在或已被删除")
    return menu


@router.delete("/{menu_id}")
async def remove_menu(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    _admin: dict = Depends(require_permission("system:menu:del")),
):
    if not await delete_menu(db, menu_id):
        raise NotFoundError("菜单不存在或已被删除")
    return {"message": "删除成功"}