"""种子数据：超级管理员 + 系统管理员 + 默认菜单 + 角色"""
import asyncio, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.core.database import async_session_factory
from app.models.user import User
from app.models.h5_user import H5User
from app.models.department import Department
from app.models.role import Role
from app.models.menu import Menu
from app.core.security import hash_password
from sqlalchemy import select

MENU_DATA = [
    # id, parent_id, name, type, path, component, permission, icon, sort
    (1,  None, "首页",       "menu",    "/dashboard",      "Dashboard",              "",               "HomeFilled",     1),
    (10, None, "系统管理",   "catalog", None,              None,                     "",               "Setting",         10),
    (11, 10,  "部门管理",   "menu",    "/departments",    "DepartmentMgr",          "system:dept:list","OfficeBuilding", 11),
    (12, 10,  "角色管理",   "menu",    "/roles",          "RoleMgr",                "system:role:list","Avatar",         12),
    (13, 10,  "用户管理",   "menu",    "/users",          "UserMgr",                "system:user:list","UserFilled",     13),
    (14, 10,  "菜单管理",   "menu",    "/menus",          "MenuMgr",                "system:menu:list","Menu",           14),
    (15, 10,  "功能控制",   "menu",    "/ws-control",     "WsControl",              "",               "Switch",          15),
    (20, None, "客户管理",   "menu",    "/h5-users",       "H5UserMgr",              "h5:user:list",   "UserFilled",      20),
    # 按钮权限 (属于系统管理子菜单)
    (101,11, "新增部门",    "button",  None,              None,                     "system:dept:add",  "",              101),
    (102,11, "编辑部门",    "button",  None,              None,                     "system:dept:edit", "",              102),
    (103,11, "删除部门",    "button",  None,              None,                     "system:dept:del",  "",              103),
    (111,12, "新增角色",    "button",  None,              None,                     "system:role:add",  "",              111),
    (112,12, "编辑角色",    "button",  None,              None,                     "system:role:edit", "",              112),
    (113,12, "删除角色",    "button",  None,              None,                     "system:role:del",  "",              113),
    (121,13, "新增用户",    "button",  None,              None,                     "system:user:add",  "",              121),
    (122,13, "编辑用户",    "button",  None,              None,                     "system:user:edit", "",              122),
    (123,13, "删除用户",    "button",  None,              None,                     "system:user:del",  "",              123),
    (131,14, "新增菜单",    "button",  None,              None,                     "system:menu:add",  "",              131),
    (132,14, "编辑菜单",    "button",  None,              None,                     "system:menu:edit", "",              132),
    (133,14, "删除菜单",    "button",  None,              None,                     "system:menu:del",  "",              133),
    # 按钮权限 (属于客户管理菜单)
    (201,20, "新增客户",    "button",  None,              None,                     "h5:user:add",      "",              201),
    (202,20, "编辑客户",    "button",  None,              None,                     "h5:user:edit",     "",              202),
    (203,20, "删除客户",    "button",  None,              None,                     "h5:user:del",      "",              203),
]


async def seed():
    async with async_session_factory() as db:
        result = await db.execute(select(User).where(User.is_super_admin == True))
        if result.scalar_one_or_none():
            print("种子数据已存在，跳过")
            return

        # 默认部门
        dept = Department(name="总公司", sort=1)
        db.add(dept)
        await db.flush()

        # 默认菜单
        for m in MENU_DATA:
            db.add(Menu(id=m[0], parent_id=m[1], name=m[2], type=m[3],
                         path=m[4], component=m[5], permission=m[6], icon=m[7], sort=m[8]))
        await db.flush()

        # 系统管理相关菜单ID（id=10系统管理目录 + 其下所有子菜单和按钮）
        system_mgmt_ids = {10, 11, 12, 13, 14, 15} | {m[0] for m in MENU_DATA if m[1] in (11, 12, 13, 14)}
        # 客户管理相关菜单ID（id=20 客户管理菜单 + 其下所有按钮）
        h5_mgmt_ids = {20} | {m[0] for m in MENU_DATA if m[1] == 20}
        # 系统管理员角色：拥有系统管理全部权限，排除客户管理（不可删除编辑）
        system_role_menu_ids = [m[0] for m in MENU_DATA if m[0] not in h5_mgmt_ids]
        system_role = Role(
            name="系统管理员",
            code="system_admin",
            description="系统管理员角色，拥有系统管理全部功能，不含H5端管理权限",
            menu_ids=str(system_role_menu_ids),
            is_system=True,
        )
        db.add(system_role)
        await db.flush()

        # 超级管理员（不参与角色控制，is_super_admin=True）
        super_admin = User(
            username="admin",
            password=hash_password("admin123456"),
            dept_id=dept.id,
            role_id=None,  # 超管不依赖角色
            is_super_admin=True,
        )
        db.add(super_admin)

        # 交付/测试账号（管理端，role=系统管理员）
        test_user = User(
            username="test",
            password=hash_password("test123"),
            dept_id=dept.id,
            role_id=system_role.id,
            is_super_admin=False,
        )
        db.add(test_user)

        # 测试 H5 用户
        h5_test = H5User(
            username="h5test",
            password=hash_password("test123"),
            name="测试用户",
            id_card="110101199001011234",
            phone="13800138000",
            bank_card="6222021234567890123",
            bank_card_name="工商银行",
            bank_card_balance=10000.00,
        )
        db.add(h5_test)

        await db.commit()
        print("种子数据创建完成！")
        print("  超级管理员: admin / admin123456")
        print("  交付账号:   test / test123 (角色: 系统管理员)")
        print("  H5测试用户: h5test / test123")


if __name__ == "__main__":
    asyncio.run(seed())