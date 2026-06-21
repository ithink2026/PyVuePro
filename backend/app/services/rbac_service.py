"""RBAC 业务逻辑 - 部门/角色/菜单管理"""

import json
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.department import Department
from app.models.role import Role
from app.models.menu import Menu


# ========== 部门 ==========
async def get_department_tree(db: AsyncSession):
    result = await db.execute(select(Department).order_by(Department.sort))
    rows = result.scalars().all()
    return [_dept_to_dict(d, rows) for d in rows if d.parent_id is None]


def _dept_to_dict(dept: Department, all_rows: list[Department]) -> dict:
    children = [_dept_to_dict(d, all_rows) for d in all_rows if d.parent_id == dept.id]
    d = {
        "id": dept.id, "name": dept.name, "parent_id": dept.parent_id,
        "sort": dept.sort, "status": dept.status,
        "created_at": dept.created_at, "updated_at": dept.updated_at,
        "children": children,
    }
    return d


async def create_department(db: AsyncSession, data: dict) -> Department:
    dept = Department(**data)
    db.add(dept)
    await db.commit()
    await db.refresh(dept)
    return dept


async def update_department(db: AsyncSession, dept_id: int, data: dict) -> Department | None:
    result = await db.execute(select(Department).where(Department.id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(dept, k, v)
    await db.commit()
    await db.refresh(dept)
    return dept


async def delete_department(db: AsyncSession, dept_id: int) -> bool:
    result = await db.execute(select(Department).where(Department.id == dept_id))
    dept = result.scalar_one_or_none()
    if not dept:
        return False
    await db.delete(dept)
    await db.commit()
    return True


# ========== 角色 ==========
async def get_role_list(db: AsyncSession, name: str = "") -> list[Role]:
    stmt = select(Role).order_by(Role.id)
    if name:
        stmt = stmt.where(Role.name.contains(name))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create_role(db: AsyncSession, data: dict) -> Role:
    role = Role(**data)
    db.add(role)
    await db.commit()
    await db.refresh(role)
    return role


async def update_role(db: AsyncSession, role_id: int, data: dict) -> Role | None:
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(role, k, v)
    await db.commit()
    await db.refresh(role)
    return role


async def delete_role(db: AsyncSession, role_id: int) -> bool:
    result = await db.execute(select(Role).where(Role.id == role_id))
    role = result.scalar_one_or_none()
    if not role:
        return False
    await db.delete(role)
    await db.commit()
    return True


# ========== 菜单 ==========
async def get_menu_tree(db: AsyncSession):
    result = await db.execute(select(Menu).order_by(Menu.sort))
    rows = result.scalars().all()
    return [_menu_to_dict(m, rows) for m in rows if m.parent_id is None]


async def get_sidebar_menu_tree(db: AsyncSession) -> list[dict]:
    """构建侧边栏菜单树（过滤掉 button 类型的子项，避免 menu 类型的菜单变成目录）"""
    tree = await get_menu_tree(db)
    _filter_button_children(tree)
    return tree


def _filter_button_children(tree: list[dict]):
    """递归过滤 children 中 type='button' 的项"""
    for item in tree:
        if item.get("children"):
            item["children"] = [c for c in item["children"] if c["type"] != "button"]
            _filter_button_children(item["children"])


def _menu_to_dict(menu: Menu, all_rows: list[Menu]) -> dict:
    children = [_menu_to_dict(m, all_rows) for m in all_rows if m.parent_id == menu.id]
    return {
        "id": menu.id, "parent_id": menu.parent_id, "name": menu.name,
        "type": menu.type, "path": menu.path, "component": menu.component,
        "permission": menu.permission, "icon": menu.icon, "sort": menu.sort,
        "visible": menu.visible, "status": menu.status,
        "created_at": menu.created_at, "updated_at": menu.updated_at,
        "children": children,
    }


async def get_menu_flat_list(db: AsyncSession) -> list[Menu]:
    result = await db.execute(select(Menu).order_by(Menu.sort))
    return list(result.scalars().all())


async def create_menu(db: AsyncSession, data: dict) -> Menu:
    menu = Menu(**data)
    db.add(menu)
    await db.commit()
    await db.refresh(menu)
    return menu


async def update_menu(db: AsyncSession, menu_id: int, data: dict) -> Menu | None:
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalar_one_or_none()
    if not menu:
        return None
    for k, v in data.items():
        if v is not None:
            setattr(menu, k, v)
    await db.commit()
    await db.refresh(menu)
    return menu


async def delete_menu(db: AsyncSession, menu_id: int) -> bool:
    result = await db.execute(select(Menu).where(Menu.id == menu_id))
    menu = result.scalar_one_or_none()
    if not menu:
        return False
    await db.delete(menu)
    await db.commit()
    return True


# ========== 权限检查 ==========
async def get_user_permissions(db: AsyncSession, user_role_id: int | None) -> list[str]:
    """获取用户角色对应的所有权限标识"""
    if user_role_id is None:
        return []
    result = await db.execute(select(Role).where(Role.id == user_role_id))
    role = result.scalar_one_or_none()
    if not role or not role.menu_ids or role.menu_ids == "[]":
        return []

    try:
        menu_ids = json.loads(role.menu_ids)
    except (json.JSONDecodeError, TypeError):
        return []

    if not menu_ids:
        return []

    result = await db.execute(select(Menu.permission).where(Menu.id.in_(menu_ids)))
    return [p for (p,) in result.all() if p]


async def get_user_menus_for_sidebar(db: AsyncSession, user_role_id: int | None) -> list[dict]:
    """获取用户有权限的侧边栏菜单"""
    if user_role_id is None:
        return []

    result = await db.execute(select(Role).where(Role.id == user_role_id))
    role = result.scalar_one_or_none()
    if not role or not role.menu_ids or role.menu_ids == "[]":
        return []

    try:
        menu_ids = json.loads(role.menu_ids)
    except (json.JSONDecodeError, TypeError):
        return []

    if not menu_ids:
        return []

    result = await db.execute(
        select(Menu).where(Menu.id.in_(menu_ids), Menu.status == 1).order_by(Menu.sort)
    )
    all_menus = list(result.scalars().all())
    # 过滤出 type in (catalog, menu) 且可见的
    all_menus = [m for m in all_menus if m.type in ("catalog", "menu") and m.visible == 1]
    all_ids = {m.id for m in all_menus}
    return [_menu_to_dict(m, all_menus) for m in all_menus if m.parent_id is None or m.parent_id not in all_ids]


async def get_assignable_menu_tree(db: AsyncSession, user_role_id: int | None) -> list[dict]:
    """获取当前用户可分配给他人的菜单树
    - 超管(role_id=None): 返回全部菜单
    - 普通用户: 返回自己拥有的菜单（含按钮），过滤掉无权看到的目录
    """
    if user_role_id is None:
        return await get_menu_tree(db)

    result = await db.execute(select(Role).where(Role.id == user_role_id))
    role = result.scalar_one_or_none()
    if not role or not role.menu_ids or role.menu_ids == "[]":
        return []

    try:
        menu_ids = json.loads(role.menu_ids)
    except (json.JSONDecodeError, TypeError):
        return []

    if not menu_ids:
        return []

    result = await db.execute(
        select(Menu).where(Menu.id.in_(menu_ids), Menu.status == 1).order_by(Menu.sort)
    )
    all_menus = list(result.scalars().all())
    all_ids = {m.id for m in all_menus}
    return [_menu_to_dict(m, all_menus) for m in all_menus if m.parent_id is None or m.parent_id not in all_ids]
