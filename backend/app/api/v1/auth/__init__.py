"""认证模块 - 管理端/H5端登录、Token刷新"""
from app.api.v1.auth.auth import router as auth_router
from app.api.v1.auth.admin_auth import router as admin_auth_router
from app.api.v1.auth.h5_auth import router as h5_auth_router