"""FastAPI 入口"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import auth as auth_router, admin_auth, h5_auth
from app.api.v1.system import admin, departments, roles, menus, users, h5_users
from app.core.config import settings
from app.core.error_handler import register_exception_handlers
from app.tasks.cleanup import heartbeat_cleanup_task
from app.utils.redis import init_redis, close_redis


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时
    await init_redis()

    # 启动心跳清理任务
    import asyncio

    cleanup_task = asyncio.create_task(heartbeat_cleanup_task())

    yield

    # 关闭时
    cleanup_task.cancel()
    await close_redis()


app = FastAPI(title="RBAC+WS API", version="1.0.0", lifespan=lifespan)

# 注册全局异常处理器
register_exception_handlers(app)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# REST API 路由
app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(admin_auth.router, prefix="/api/v1")
app.include_router(h5_auth.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(h5_users.router, prefix="/api/v1")
app.include_router(departments.router, prefix="/api/v1")
app.include_router(roles.router, prefix="/api/v1")
app.include_router(menus.router, prefix="/api/v1")
app.include_router(admin.router, prefix="/api/v1")

# WebSocket 路由（根据开关决定是否注册）
if settings.ENABLE_WEBSOCKET:
    from app.api.ws import h5, admin as ws_admin

    app.include_router(h5.router)
    app.include_router(ws_admin.router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
