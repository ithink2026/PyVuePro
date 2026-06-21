"""系统管理模块 - 管理员信息、部门/角色/用户/菜单管理"""
from app.api.v1.system.admin import router as admin_router
from app.api.v1.system.departments import router as departments_router
from app.api.v1.system.roles import router as roles_router
from app.api.v1.system.users import router as users_router
from app.api.v1.system.menus import router as menus_router