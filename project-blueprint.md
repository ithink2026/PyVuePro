# 项目技术蓝图：H5 操作页 + 管理端实时监控系统

> 本文档是项目技术选型与架构的完整总结，用于后续 AI 辅助开发时提供上下文。每次开启新的 AI 开发会话时，将本文档作为上下文输入，即可快速对齐技术方案。

---

## 1. 项目概述

一个 H5 操作页面 + 后台管理端的 Web 应用系统，核心功能：

- **H5 端**：用户通过 uni-app 构建的移动端页面访问操作页，与后端保持 WebSocket 长连接
- **管理端**：后台管理员实时查看各个操作页面的在线人数，同一账号只能在一处登录（互斥登录）
- **账号隔离**：管理端账号与 H5 端账号完全分离，H5 用户无法登录管理端，反之亦然
- **实时性**：在线人数变化即时推送到管理端，无需手动刷新

---

## 2. 技术栈总览

### 2.1 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.5+ | 前端框架，Composition API 写法 |
| Vite | 6+ | 管理端构建工具 |
| Vue Router | 4.4+ | 路由管理 |
| Pinia | 2.2+ | 状态管理 |
| **uni-app** | 3.x (Vue3版) | **H5 端**跨端开发框架，支持 H5 + 小程序 + App |
| **uview-plus** | 3.x | **H5 端** uni-app 生态 UI 组件库，Vue3 版 |
| Element Plus | 2.9+ | **管理端**桌面端 UI 组件库 |
| ECharts | 5.5+ | 管理端图表（在线人数趋势等） |
| Axios | 1.7+ | HTTP 请求 |
| 原生 WebSocket | — | 实时通信，浏览器原生 API，无需额外依赖 |
| HBuilderX | 最新版 | uni-app 官方 IDE（开发 H5 端，也可用 CLI） |

### 2.2 后端

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 开发语言 |
| FastAPI | 0.115+ | Web 框架，原生支持 WebSocket + 异步 |
| Uvicorn | 0.34+ | ASGI 服务器 |
| PyJWT | 2.10+ | JWT 鉴权，生成和校验登录 Token |
| passlib + bcrypt | 1.7+ | 密码哈希存储 |
| SQLAlchemy | 2.0+ | ORM，操作数据库 |
| Alembic | 1.14+ | 数据库迁移，版本化管理表结构 |
| redis-py（异步） | 5+ | Redis 客户端，在线状态、会话、Pub/Sub |
| Pydantic | 2+ | 数据校验，FastAPI 内置 |
| pydantic-settings | 2+ | 环境变量与配置管理（替代 python-dotenv） |

### 2.3 数据库与缓存

| 技术 | 用途 | 存储内容 |
|------|------|---------|
| MySQL 8.0 | 关系型数据库 | 用户表（含 role 字段区分 admin/h5）、操作日志、业务数据 |
| Redis 7 | 内存缓存 | 在线用户心跳、管理端会话、互斥登录状态 |

### 2.4 部署

| 技术 | 用途 |
|------|------|
| Nginx | 反向代理、WebSocket 代理、HTTPS、静态资源 |
| Docker + Docker Compose | 一键部署，环境隔离 |
| Let's Encrypt / acme.sh | 免费 SSL 证书，自动续期 |
| 轻量云服务器 | 2核2G 起步，腾讯云/阿里云均可 |

---

## 3. 系统架构

```
┌─────────────────────────────────────────────────┐
│                    客户端                         │
│  ┌──────────────────┐      ┌──────────────────────┐ │
│  │  H5 端 (uni-app   │      │  管理端 (Vue3        │ │
│  │  + uview-plus)   │      │  + Element Plus)     │ │
│  └──────┬───────┘      └──────────┬───────────┘ │
│         │ WebSocket                │ WebSocket   │
│         │ + HTTP                   │ + HTTP      │
└─────────┼──────────────────────────┼─────────────┘
          │                          │
┌─────────▼──────────────────────────▼─────────────┐
│                   Nginx (HTTPS/WSS)               │
└──────────────────────┬───────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────┐
│               FastAPI + Uvicorn                   │
│  ┌──────────┐ ┌───────────┐ ┌─────────────────┐ │
│  │ REST API │ │ WS /ws/h5 │ │ WS /ws/admin    │ │
│  │ (登录/CRUD)│ │ (H5心跳)  │ │ (管理端推送)    │ │
│  └──────────┘ └─────┬─────┘ └────────┬────────┘ │
│                      │               │           │
│              ┌───────▼───────┐       │           │
│              │  Redis        │◄──────┘           │
│              │  - 在线心跳    │                   │
│              │  - 互斥登录    │                   │
│              │  - Pub/Sub    │                   │
│              └───────────────┘                   │
│  ┌──────────────────────┐                        │
│  │  SQLAlchemy ORM      │                        │
│  └──────────┬───────────┘                        │
└─────────────┼────────────────────────────────────┘
              │
┌─────────────▼───────────┐
│        MySQL 8.0        │
│  - 用户表（含 role 字段）  │
│  - 业务数据表           │
│  - 操作日志表           │
└─────────────────────────┘
```

---

## 4. 目录结构

```
project/
├── backend/                         # Python 后端
│   ├── main.py                      # FastAPI 入口，启动事件
│   ├── requirements.txt             # Python 依赖
│   ├── .env                         # 环境变量（数据库密码等，不提交 Git）
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── v1/                  # HTTP REST API
│   │   │   │   ├── __init__.py
│   │   │   │   ├── auth.py          # 登录、登出、Token 刷新（admin/h5 共用逻辑）
│   │   │   │   ├── admin_auth.py    # 管理端登录端点（POST /auth/admin/login）
│   │   │   │   ├── h5_auth.py       # H5 端登录端点（POST /auth/h5/login）
│   │   │   │   └── users.py         # 用户 CRUD
│   │   │   └── ws/                  # WebSocket 端点
│   │   │       ├── __init__.py
│   │   │       ├── h5.py            # H5 端 WebSocket（心跳）
│   │   │       └── admin.py         # 管理端 WebSocket（推送）
│   │   ├── models/                  # SQLAlchemy 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   └── base.py             # 模型基类
│   │   ├── schemas/                 # Pydantic 请求/响应模型
│   │   │   ├── __init__.py
│   │   │   ├── auth.py
│   │   │   └── user.py
│   │   ├── core/                    # 核心配置
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # 配置类（读取 .env）
│   │   │   ├── security.py         # JWT 生成/校验、密码哈希
│   │   │   └── database.py         # 数据库连接、Session 管理
│   │   ├── services/               # 业务逻辑层
│   │   │   ├── __init__.py
│   │   │   ├── auth_service.py
│   │   │   ├── online_service.py   # 在线人数统计逻辑
│   │   │   └── user_service.py
│   │   ├── tasks/                   # 后台定时任务
│   │   │   ├── __init__.py
│   │   │   └── cleanup.py          # 定时清理过期心跳（30s 扫描，60s 超时剔除）
│   │   └── utils/                   # 工具函数
│   │       ├── __init__.py
│   │       └── redis.py            # Redis 连接管理
│   └── alembic/                     # 数据库迁移
│       ├── env.py
│       └── versions/
│
├── frontend-admin/                  # 管理端（Vue 3 + Element Plus）
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.ts                  # 入口
│       ├── App.vue
│       ├── router/
│       │   └── index.ts
│       ├── stores/
│       │   ├── auth.ts              # 登录状态
│       │   └── online.ts            # 在线人数状态
│       ├── views/
│       │   ├── Login.vue            # 登录页
│       │   └── Dashboard.vue        # 仪表盘（在线人数面板）
│       ├── components/
│       │   └── OnlineCounter.vue    # 在线人数组件
│       └── utils/
│           ├── request.ts           # Axios 封装（拦截器、Token）
│           └── websocket.ts         # WebSocket 封装（重连、心跳）
│
├── frontend-h5/                     # H5 端（uni-app + Vue 3 + uview-plus）
│   ├── package.json
│   ├── vite.config.ts
│   ├── pages.json                   # uni-app 页面路由配置
│   ├── manifest.json                # uni-app 应用配置
│   ├── uni.scss                     # uni-app 全局样式变量
│   ├── App.vue                      # 应用入口
│   ├── main.ts                      # 主入口
│   ├── index.html
│   ├── pages/                       # 页面目录（uni-app 规范）
│   │   └── operation/
│   │       └── index.vue            # 操作页面
│   ├── components/                  # 公共组件
│   ├── stores/                      # Pinia 状态管理
│   │   └── user.ts
│   ├── utils/
│   │   ├── request.ts               # Axios 封装（uni.request 适配）
│   │   └── websocket.ts             # WebSocket 封装（心跳、重连）
│   └── static/                      # 静态资源
│
├── nginx/
│   └── nginx.conf                   # Nginx 配置
├── docker-compose.yml               # Docker 编排
└── .gitignore
```

---

## 5. 核心功能实现要点

### 5.1 在线人数实时监控

**流程**：H5 端建立 WebSocket → 每 30 秒发心跳 → 后端写 Redis → 管理端实时推送

```
H5 端                         后端                       管理端
  │                             │                          │
  │── WS Connect ──────────────►│                          │
  │                             │── 记录在线 ──► Redis     │
  │                             │── 广播人数 ────────────►│
  │── ping(每30s) ─────────────►│                          │
  │                             │── 更新心跳时间 ──► Redis │
  │                             │── 广播人数 ────────────►│
  │         (断开)              │                          │
  │                             │── 60s无心跳 → 剔除      │
  │                             │── 广播人数 ────────────►│
```

**Redis 数据结构**：

```
Key: online_users              → Hash
  field: user_123              → 心跳时间戳 (float)
  field: user_456              → 心跳时间戳 (float)

// 如果需要按页面区分
Key: online_users:{page_id}    → Hash
```

**后端定时清理**：每 30 秒扫描一次，超过 60 秒无心跳的用户自动剔除，并广播更新。

### 5.2 互斥登录（同一账号只能一处登录）

**适用范围**：管理端和 H5 端均适用，同一账号在两端的登录互斥独立管理。

**流程**：

```
用户 A 登录 ──► Redis 记录: sessions:{user_type} → {username: ws_id_A}
                                       │
用户 B 同账号登录 ──► 检测到已有 ws_id_A
                     │
                     ├── Redis Pub/Sub 发踢人消息
                     ├── A 的 WebSocket 收到 kicked 通知
                     ├── A 前端弹窗"账号已在其他设备登录"并跳转登录页
                     └── Redis 更新: {username: ws_id_B}
```

**Redis 数据结构**：

```
# 管理端会话
Key: admin_sessions            → Hash
  field: admin_zhangsan        → ws_id (当前有效连接标识)

# H5 端会话
Key: h5_sessions               → Hash
  field: user_123              → ws_id (当前有效连接标识)
```

### 5.3 WebSocket 断线重连

两端（H5 和管理端）都需要实现指数退避重连：

```
重连策略：
  第1次：等待 1 秒
  第2次：等待 2 秒
  第3次：等待 4 秒
  ...
  最大：等待 30 秒
  连接成功后重置计数器
```

### 5.4 JWT 鉴权与账号隔离

- 登录成功返回 `access_token`（短期，如 30 分钟）和 `refresh_token`（长期，如 7 天）
- JWT Payload 中包含 `role` 字段（`admin` 或 `h5`），用于后续请求的权限校验
- HTTP 请求：`Authorization: Bearer <access_token>`
- **登录端点分离**：
  - 管理端登录：`POST /api/v1/auth/admin/login` — 仅 `role=admin` 用户可登录，H5 用户被拒绝
  - H5 端登录：`POST /api/v1/auth/h5/login` — 仅 `role=h5` 用户可登录，管理端用户被拒绝
- WebSocket 连接：连接建立后，客户端首条消息发送 `{"type": "auth", "token": "xxx"}`，后端验证 Token 并校验 role 是否匹配当前 WS 端点（`/ws/admin` 仅接受 admin，`/ws/h5` 仅接受 h5）
- 后端 WebSocket 连接建立后设置 10 秒认证超时，超时未收到有效 Token 则主动断开连接

### 5.5 账号隔离设计

**核心原则**：管理端（admin）和 H5 端（h5）是两套完全独立的账号体系，互不通用。

**用户表设计**：

```sql
-- users 表核心字段
id          BIGINT PRIMARY KEY AUTO_INCREMENT,
username    VARCHAR(64)  NOT NULL UNIQUE,
password    VARCHAR(256) NOT NULL,           -- bcrypt 哈希
role        ENUM('admin', 'h5') NOT NULL,    -- 账号类型：admin=管理端，h5=H5端
created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
```

**登录校验流程**：

```
H5 用户登录                           后端
  │                                    │
  │── POST /api/v1/auth/h5/login ────►│
  │                                    │── 查询用户 → role=h5 ✓
  │◄─── 200 { access_token, ... } ────│

H5 用户尝试登录管理端
  │                                    │
  │── POST /api/v1/auth/admin/login ─►│
  │                                    │── 查询用户 → role=h5 ✗
  │◄─── 403 "该账号无权登录管理端" ────│
```

**后端校验中间件**：

```python
# 登录接口校验（auth_service.py）
async def login(username: str, password: str, required_role: str) -> dict:
    user = await get_user_by_username(username)
    if not user or not verify_password(password, user.password):
        raise HTTPException(401, "用户名或密码错误")
    if user.role != required_role:
        raise HTTPException(403, f"该账号无权登录{'管理端' if required_role == 'admin' else 'H5端'}")
    return create_tokens(user)  # JWT payload 中包含 role

# WebSocket 校验（ws/ 端点通用）
async def ws_auth(websocket, required_role: str) -> User:
    msg = await asyncio.wait_for(websocket.receive_json(), timeout=10)
    payload = verify_token(msg["token"])
    if payload["role"] != required_role:
        await websocket.close(4003, "无权访问此端点")
        return None
    return await get_user_by_id(payload["user_id"])
```

**各端 API 权限矩阵**：

| API 端点 | 允许角色 | 说明 |
|---------|---------|------|
| `POST /api/v1/auth/admin/login` | `admin` | 管理端登录 |
| `POST /api/v1/auth/h5/login` | `h5` | H5 端登录 |
| `POST /api/v1/auth/refresh` | `admin`, `h5` | Token 刷新（通用） |
| `WS /ws/admin` | `admin` | 管理端实时推送 |
| `WS /ws/h5` | `h5` | H5 端心跳 |
| `GET /api/v1/admin/*` | `admin` | 管理端业务 API |
| `GET /api/v1/h5/*` | `h5` | H5 端业务 API |

---

## 6. 依赖清单

### 6.1 后端 `requirements.txt`

```
fastapi==0.115.*
uvicorn[standard]==0.34.*
redis[hiredis]==5.*
sqlalchemy==2.0.*
alembic==1.14.*
pyjwt==2.10.*
passlib[bcrypt]==1.7.*
pydantic==2.*
pydantic-settings==2.*
pymysql==1.1.*
```

### 6.2 管理端 `package.json`

```json
{
  "dependencies": {
    "vue": "^3.5",
    "vue-router": "^4.4",
    "pinia": "^2.2",
    "element-plus": "^2.9",
    "echarts": "^5.5",
    "axios": "^1.7"
  },
  "devDependencies": {
    "vite": "^6.0",
    "@vitejs/plugin-vue": "^5.2",
    "unplugin-auto-import": "^0.18",
    "unplugin-vue-components": "^0.27"
  }
}
```

### 6.3 H5 端 `package.json`（uni-app + uview-plus）

```json
{
  "dependencies": {
    "vue": "^3.5",
    "pinia": "^2.2",
    "uview-plus": "^3.5",
    "axios": "^1.7"
  },
  "devDependencies": {
    "@dcloudio/types": "^3.4",
    "@dcloudio/uni-app": "3.x",
    "@dcloudio/uni-app-plus": "3.x",
    "@dcloudio/uni-components": "3.x",
    "@dcloudio/uni-h5": "3.x",
    "@dcloudio/uni-mp-weixin": "3.x",
    "@dcloudio/vite-plugin-uni": "^3.0",
    "sass": "^1.80",
    "vite": "^6.0"
  }
}
```

---

## 7. 关键配置

### 7.1 Nginx WebSocket 代理

```nginx
# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name example.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    http2 on;
    server_name example.com;

    ssl_certificate     /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    # 安全头
    add_header Strict-Transport-Security "max-age=63072000" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;

    # 管理端静态资源
    location /admin {
        alias /var/www/admin;
        try_files $uri $uri/ /admin/index.html;
    }

    # H5 端静态资源（uni-app H5 构建产物）
    location /h5 {
        alias /var/www/h5;
        try_files $uri $uri/ /h5/index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 86400s;   # 24小时，避免空闲断开
        proxy_send_timeout 86400s;
    }
}
```

### 7.2 Docker Compose

```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    env_file:
      - .env.docker                    # 从文件读取敏感信息，不硬编码
    environment:
      - DATABASE_URL=mysql+pymysql://${MYSQL_USER}:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy

  mysql:
    image: mysql:8.0
    command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
    environment:
      MYSQL_ROOT_PASSWORD: ${MYSQL_ROOT_PASSWORD}
      MYSQL_DATABASE: ${MYSQL_DATABASE}
      MYSQL_USER: ${MYSQL_USER}        # 创建应用专用用户
      MYSQL_PASSWORD: ${MYSQL_PASSWORD}
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 5s
      retries: 5

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf
      - ./frontend-admin/dist:/var/www/admin
      - ./frontend-h5/dist/build/h5:/var/www/h5
      - ./ssl:/etc/ssl
    depends_on:
      - backend

volumes:
  mysql_data:
```

配套 `.env.docker` 文件（不提交 Git）：

```bash
# .env.docker
MYSQL_ROOT_PASSWORD=change_me_root_pass
MYSQL_DATABASE=dbname
MYSQL_USER=app_user
MYSQL_PASSWORD=change_me_app_pass
REDIS_PASSWORD=change_me_redis_pass
```

### 7.3 服务器参数

```bash
# 文件描述符上限
ulimit -n 65535

# 内核参数 /etc/sysctl.conf
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 8192
net.ipv4.tcp_tw_reuse = 1
```

---

## 8. 启动命令

```bash
# 后端
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

# 前端管理端
cd frontend-admin
npm install && npm run dev

# 前端 H5 端（uni-app）
cd frontend-h5
npm install
# 开发模式（H5 浏览器预览）
npm run dev:h5
# 生产构建（H5）
npm run build:h5

# Docker 一键部署
docker compose up -d
```

---

## 9. 长连接功能开关

系统支持通过配置开关来控制 WebSocket 长连接功能的启用/关闭，方便在不需要实时监控的场景下关闭该功能以节省服务器资源。

### 9.1 开关位置

**后端 `.env` 文件**：

```bash
# .env
# 长连接功能开关：true=启用，false=关闭
ENABLE_WEBSOCKET=true
```

### 9.2 后端实现

```python
# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    ENABLE_WEBSOCKET: bool = True  # 默认开启

settings = Settings()
```

```python
# main.py
from app.core.config import settings

# 根据开关决定是否注册 WebSocket 路由
if settings.ENABLE_WEBSOCKET:
    from app.api.ws import h5, admin
    app.include_router(h5.router)
    app.include_router(admin.router)
```

```python
# services/online_service.py —— 业务逻辑中也可根据开关跳过
from app.core.config import settings

async def record_heartbeat(user_id: str):
    if not settings.ENABLE_WEBSOCKET:
        return  # 长连接关闭时跳过心跳记录
    await redis_client.hset(ONLINE_USERS_KEY, user_id, time.time())
```

### 9.3 前端适配

前端通过后端 API 获取开关状态，决定是否建立 WebSocket 连接：

```typescript
// utils/api.ts —— 新增一个获取开关状态的接口
// GET /api/v1/config/websocket-enabled → { "enabled": true }
```

```typescript
// utils/websocket.ts
import { getWebSocketConfig } from './api'

export async function initWebSocket(userId: string) {
  const { enabled } = await getWebSocketConfig()
  if (!enabled) {
    console.log('长连接功能已关闭，跳过 WebSocket 连接')
    return
  }
  // 正常建立 WebSocket 连接...
}
```

### 9.4 切换效果

| 开关状态 | 后端行为 | 前端行为 |
|---------|---------|---------|
| `ENABLE_WEBSOCKET=true` | 注册 WebSocket 路由，记录心跳，推送在线人数 | 建立 WebSocket 连接，发送心跳 |
| `ENABLE_WEBSOCKET=false` | 不注册 WebSocket 路由，跳过心跳记录 | 不建立 WebSocket 连接，页面正常使用 |

修改 `.env` 后重启后端服务即可生效，无需改代码、无需重新部署。

---

## 10. AI 开发使用说明

将此文档作为 AI 开发会话的上下文输入，配合以下提示词模板使用：

> 我正在开发一个项目，请先阅读项目技术蓝图 `/workspace/project-blueprint.md`，然后帮我实现 [具体功能]。
> 技术栈：Python FastAPI + Vue 3 + uni-app + MySQL + Redis
> 请遵循文档中的技术选型、目录结构和代码规范。

也可以按模块拆分开发：

- **初始化项目脚手架**：后端 FastAPI 项目结构 + 前端 Vue 项目结构
- **用户认证模块**：登录/注册 API + JWT + 管理端登录页
- **H5 操作页面**：uni-app 页面 + uview-plus 组件 + WebSocket 心跳
- **管理端仪表盘**：Element Plus 布局 + 在线人数实时面板
- **互斥登录**：Redis 会话管理 + 被踢下线通知
- **部署配置**：Nginx + Docker Compose + 环境变量