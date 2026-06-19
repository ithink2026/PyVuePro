# 项目技术蓝图：H5 操作页 + 管理端实时监控系统

> 本文档是项目技术选型与架构的完整总结，用于后续 AI 辅助开发时提供上下文。每次开启新的 AI 开发会话时，将本文档作为上下文输入，即可快速对齐技术方案。

---

## 1. 项目概述

一个 H5 操作页面 + 后台管理端的 Web 应用系统，核心功能：

- **H5 端**：用户在移动端浏览器中访问操作页面，与后端保持 WebSocket 长连接
- **管理端**：后台管理员实时查看各个操作页面的在线人数，同一账号只能在一处登录（互斥登录）
- **实时性**：在线人数变化即时推送到管理端，无需手动刷新

---

## 2. 技术栈总览

### 2.1 前端

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue 3 | 3.5+ | 前端框架，Composition API 写法 |
| Vite | 6+ | 构建工具 |
| Vue Router | 4.4+ | 路由管理 |
| Pinia | 2.2+ | 状态管理 |
| Vant 4 | 4.9+ | **H5 端**移动端 UI 组件库 |
| Element Plus | 2.9+ | **管理端**桌面端 UI 组件库 |
| ECharts | 5.5+ | 管理端图表（在线人数趋势等） |
| Axios | 1.7+ | HTTP 请求 |
| 原生 WebSocket | — | 实时通信，浏览器原生 API，无需额外依赖 |

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
| python-dotenv | 1+ | 环境变量管理 |

### 2.3 数据库与缓存

| 技术 | 用途 | 存储内容 |
|------|------|---------|
| MySQL 8.0 | 关系型数据库 | 用户表、操作日志、业务数据 |
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
│  ┌──────────────┐      ┌──────────────────────┐ │
│  │  H5 端 (Vue3  │      │  管理端 (Vue3        │ │
│  │  + Vant4)    │      │  + Element Plus)     │ │
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
│  - 用户表               │
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
│   │   │   │   ├── auth.py          # 登录、登出、Token 刷新
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
├── frontend-h5/                     # H5 端（Vue 3 + Vant 4）
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   └── src/
│       ├── main.ts
│       ├── App.vue
│       ├── router/
│       │   └── index.ts
│       ├── views/
│       │   └── OperationPage.vue    # 操作页面
│       └── utils/
│           ├── request.ts           # Axios 封装
│           └── websocket.ts         # WebSocket 封装（心跳、重连）
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

**流程**：

```
管理端 A 登录 ──► Redis 记录: admin_sessions → {username: ws_id_A}
                                       │
管理端 B 同账号登录 ──► 检测到已有 ws_id_A
                     │
                     ├── Redis Pub/Sub 发踢人消息
                     ├── A 的 WebSocket 收到 kicked 通知
                     ├── A 前端弹窗"被踢下线"并跳转登录页
                     └── Redis 更新: {username: ws_id_B}
```

**Redis 数据结构**：

```
Key: admin_sessions            → Hash
  field: admin_zhangsan        → ws_id (当前有效连接标识)
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

### 5.4 JWT 鉴权

- 登录成功返回 `access_token`（短期，如 30 分钟）和 `refresh_token`（长期，如 7 天）
- HTTP 请求：`Authorization: Bearer <access_token>`
- WebSocket 连接：在 URL 参数中传递 Token：`ws://host/ws/h5/user123?token=xxx`
- 后端 WebSocket 连接建立时校验 Token，不合法则拒绝连接

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
python-dotenv==1.*
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

### 6.3 H5 端 `package.json`

```json
{
  "dependencies": {
    "vue": "^3.5",
    "vue-router": "^4.4",
    "pinia": "^2.2",
    "vant": "^4.9",
    "axios": "^1.7"
  },
  "devDependencies": {
    "vite": "^6.0",
    "@vitejs/plugin-vue": "^5.2",
    "unplugin-vue-components": "^0.27",
    "@vant/auto-import-resolver": "^1.2"
  }
}
```

---

## 7. 关键配置

### 7.1 Nginx WebSocket 代理

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate     /etc/ssl/cert.pem;
    ssl_certificate_key /etc/ssl/key.pem;

    # 管理端静态资源
    location /admin {
        alias /var/www/admin;
        try_files $uri $uri/ /admin/index.html;
    }

    # H5 端静态资源
    location /h5 {
        alias /var/www/h5;
        try_files $uri $uri/ /h5/index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # WebSocket 代理
    location /ws/ {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400s;   # 24小时，避免空闲断开
        proxy_send_timeout 86400s;
    }
}
```

### 7.2 Docker Compose

```yaml
version: "3.8"
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://user:pass@mysql:3306/dbname
      - REDIS_URL=redis://redis:6379
    depends_on:
      mysql:
        condition: service_healthy
      redis:
        condition: service_healthy

  mysql:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpass
      MYSQL_DATABASE: dbname
    volumes:
      - mysql_data:/var/lib/mysql
    healthcheck:
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost"]
      interval: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
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
      - ./frontend-h5/dist:/var/www/h5
      - ./ssl:/etc/ssl
    depends_on:
      - backend

volumes:
  mysql_data:
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

# 前端 H5 端
cd frontend-h5
npm install && npm run dev

# Docker 一键部署
docker compose up -d
```

---

## 9. 费用估算

| 项目 | 方案 | 首年费用 |
|------|------|---------|
| 云服务器（2核2G） | 腾讯云/阿里云轻量 | ¥38（新用户） |
| 域名 .cn | 腾讯云/阿里云 | ¥28-33（首年） |
| Redis | 自建 Docker | ¥0 |
| SSL 证书 | 免费（Let's Encrypt / 云厂商） | ¥0 |
| MySQL | 自建 Docker | ¥0 |
| **合计** | | **¥66-71/年** |

续费约 ¥100-150/年。

---

## 10. AI 开发使用说明

将此文档作为 AI 开发会话的上下文输入，配合以下提示词模板使用：

> 我正在开发一个项目，请先阅读项目技术蓝图 `/workspace/project-blueprint.md`，然后帮我实现 [具体功能]。
> 技术栈：Python FastAPI + Vue 3 + MySQL + Redis
> 请遵循文档中的技术选型、目录结构和代码规范。

也可以按模块拆分开发：

- **初始化项目脚手架**：后端 FastAPI 项目结构 + 前端 Vue 项目结构
- **用户认证模块**：登录/注册 API + JWT + 管理端登录页
- **H5 操作页面**：Vant 4 页面 + WebSocket 心跳
- **管理端仪表盘**：Element Plus 布局 + 在线人数实时面板
- **互斥登录**：Redis 会话管理 + 被踢下线通知
- **部署配置**：Nginx + Docker Compose + 环境变量