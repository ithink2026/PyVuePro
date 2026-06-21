# RBAC+WS系统

## 1. 项目概述

RBAC+WS系统是一套面向企业级场景的全栈管理平台，提供管理后台（Admin）和移动端（H5）两个前端入口，配合统一的后端 API 服务，实现用户管理、权限控制、实时在线监控等核心功能。

**主要功能**：
- **管理后台**：基于 RBAC（角色-权限）模型的系统管理，支持部门、角色、用户、菜单的 CRUD 及细粒度按钮级权限控制。
- **H5 移动端**：面向业务操作人员，提供登录认证与业务操作页面。
- **实时在线监控**：通过 WebSocket 长连接实现 H5 用户在线状态实时统计，管理端 Dashboard 可查看当前在线人数。
- **JWT 双 Token 认证**：Access Token + Refresh Token 机制，保障接口安全。

**价值定位**：为业务提供统一、安全、可扩展的管理平台，支持多角色协作，适用于企业权限管理、实时监控等场景。

---

## 2. 技术架构

### 2.1 前端技术栈

#### 管理后台（frontend-admin）

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | ^3.5 | 渐进式前端框架 |
| Vite | ^6.0 | 构建工具 |
| TypeScript | ^5.6 | 类型安全 |
| Vue Router | ^4.4 | 路由管理 |
| Pinia | ^2.2 | 状态管理 |
| Element Plus | ^2.9 | UI 组件库 |
| ECharts | ^5.5 | 数据可视化 |
| Axios | ^1.7 | HTTP 请求库 |
| unplugin-auto-import | ^0.18 | 自动导入 API |
| unplugin-vue-components | ^0.27 | 自动导入组件 |

#### H5 移动端（frontend-h5）

| 技术 | 版本 | 说明 |
|------|------|------|
| Vue | ^3.5 | 渐进式前端框架 |
| uni-app | 3.0.0-alpha | 跨端开发框架 |
| Pinia | ^2.2 | 状态管理 |
| uView Plus | ^3.5 | UI 组件库 |
| Vite | 5.2.8 | 构建工具 |
| Sass | ^1.80 | CSS 预处理器 |

### 2.2 后端技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Python | 3.11 | 编程语言 |
| FastAPI | 0.115.* | 异步 Web 框架 |
| Uvicorn | 0.34.* | ASGI 服务器 |
| SQLAlchemy | 2.0.* | 异步 ORM |
| Alembic | 1.14.* | 数据库迁移 |
| MySQL | 8.0 | 关系型数据库 |
| Redis | 7.x | 缓存/在线状态存储 |
| PyJWT | 2.10.* | JWT 认证 |
| Passlib + bcrypt | 1.7.* | 密码哈希 |
| Pydantic | 2.* | 数据校验 |
| Pydantic-Settings | 2.* | 配置管理 |

### 2.3 基础设施

| 技术 | 说明 |
|------|------|
| Docker Compose | 容器编排 |
| Nginx | 反向代理 + 静态资源服务 |
| WebSocket | 实时双向通信 |

---

## 3. 功能模块

### 3.1 认证授权模块

- **双 Token 机制**：Access Token（30 分钟有效）用于接口鉴权，Refresh Token（7 天有效）用于无感刷新。
- **端隔离机制**：管理端用户与 H5 端用户分别存储于独立的数据库表（`users` 和 `h5_users`），物理隔离。管理端登录仅查询 `users` 表，H5 端登录仅查询 `h5_users` 表，JWT Token 中携带 `port` 标识（`admin`/`h5`）进行访问控制。
- **密码安全**：bcrypt 哈希存储，支持修改密码与重置密码功能。

### 3.2 RBAC 权限管理模块

系统实现了完整的基于角色的访问控制（RBAC），包含以下子模块：

- **部门管理**：支持树形部门结构，可增删改查，支持启用/禁用。
- **角色管理**：支持创建角色、分配菜单权限（通过菜单 ID 列表），系统角色不可删除。
- **用户管理**：管理后台用户（`users` 表），支持关联部门和角色，支持重置密码。默认不显示超级管理员。管理端仅可创建管理端用户，禁止创建 H5 用户。
- **菜单管理**：三级菜单结构（目录 → 菜单 → 按钮），支持路由、组件、权限标识、图标配置。

**权限标识示例**：`system:user:list`、`system:user:add`、`system:role:delete` 等。

### 3.3 超级管理员

- 系统内置超级管理员账号（默认 `admin / admin123456`），`is_super_admin=True`。
- 超级管理员不参与 RBAC 角色控制，拥有全部权限。
- 种子数据脚本自动创建超级管理员及默认菜单、系统角色。

### 3.4 WebSocket 实时在线统计

- **H5 端**：通过 WebSocket 发送心跳（`ping`/`pong`），后端记录在线状态到 Redis。
- **管理端**：Dashboard 通过 WebSocket 接收实时推送的在线人数。
- **心跳清理**：后台定时任务定期清理过期心跳（默认 60 秒超时），自动更新在线人数。
- **功能开关**：可通过配置 `ENABLE_WEBSOCKET` 和 `SHOW_ONLINE_COUNT` 控制功能启停。

### 3.5 功能控制

管理后台提供 WebSocket 功能开关的可视化控制页面（WsControl），便于运维人员动态管理。

### 3.6 H5 用户管理模块

H5 端用户因包含姓名、身份证号、手机号、银行卡号等敏感个人信息，使用独立的 `h5_users` 表存储，与管理端用户完全物理隔离。

- **独立表结构**：`h5_users` 表包含 `name`、`id_card`、`phone`、`bank_card` 等敏感字段。
- **独立管理界面**：管理后台左侧菜单"**H5端管理** → **H5用户管理**"，与系统管理中的用户管理完全分离，拥有独立的数据视图和权限控制。
- **独立权限体系**：`h5:user:list`、`h5:user:add`、`h5:user:edit`、`h5:user:del` 四个权限标识，与系统管理的 `system:user:*` 权限互不干扰。
- **数据安全**：管理端系统管理模块中不包含任何 H5 用户的新增、编辑功能入口，确保两类用户数据逻辑分离。

---

## 4. 环境要求

### 4.1 本地开发环境

| 软件 | 最低版本 | 说明 |
|------|----------|------|
| Python | 3.11+ | 后端运行环境 |
| Node.js | 18+ | 前端构建环境 |
| MySQL | 8.0 | 数据库 |
| Redis | 7.0+ | 缓存服务 |
| npm | 9+ | 包管理工具 |

### 4.2 部署环境

| 软件 | 说明 |
|------|------|
| Docker | 20.10+ |
| Docker Compose | 2.0+ |

---

## 5. 本地启动

### 5.1 克隆项目

```bash
git clone <repository-url>
cd code
```

### 5.2 后端启动

#### ① 创建 Python 虚拟环境

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

#### ② 安装依赖

```bash
pip install -r requirements.txt
```

#### ③ 配置环境变量

在 `backend/` 目录下创建 `.env` 文件：

```env
# 数据库连接
DATABASE_URL=mysql+pymysql://root:root@localhost:3306/subsidy

# Redis 连接
REDIS_URL=redis://localhost:6379

# JWT 配置
JWT_SECRET_KEY=your-random-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# WebSocket 开关
ENABLE_WEBSOCKET=true

# 首页在线统计开关
SHOW_ONLINE_COUNT=true

# 心跳超时（秒）
HEARTBEAT_TIMEOUT=60
HEARTBEAT_CLEANUP_INTERVAL=30
```

#### ④ 创建数据库

```sql
CREATE DATABASE subsidy CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

#### ⑤ 运行数据库迁移

```bash
cd backend
alembic upgrade head
```

#### ⑥ 初始化种子数据

```bash
python scripts/seed_rbac.py
```

#### ⑦ 启动后端服务

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### ⑧ 验证后端

访问 [http://localhost:8000/health](http://localhost:8000/health)，返回 `{"status": "ok"}` 表示启动成功。

访问 [http://localhost:8000/docs](http://localhost:8000/docs) 可查看 Swagger API 文档。

### 5.3 前端管理后台启动

```bash
cd frontend-admin
npm install
npm run dev
```

访问 [http://localhost:3000](http://localhost:3000)，使用默认账号 `admin / admin123456` 登录。

### 5.4 前端 H5 移动端启动

```bash
cd frontend-h5
npm install

# H5 模式
npm run dev:h5

# 微信小程序模式
npm run dev:mp-weixin
```

H5 模式访问 [http://localhost:3001](http://localhost:3001)。

---

## 6. 线上部署

### 6.1 部署架构

```
┌──────────────────────────────────────────────┐
│                   Nginx (:80/:443)            │
│  /admin → 管理端静态资源    /h5 → H5 静态资源  │
│  /api/* → 后端 API 代理    /ws/* → WebSocket  │
└─────────────────┬────────────────────────────┘
                  │
    ┌─────────────┼─────────────┐
    │             │             │
    ▼             ▼             ▼
┌───────┐   ┌──────────┐   ┌───────┐
│ MySQL │   │  Backend │   │ Redis │
│ :3306 │   │  :8000   │   │ :6379 │
└───────┘   └──────────┘   └───────┘
```

### 6.2 部署步骤

#### ① 准备环境变量

在项目根目录创建 `.env.docker` 文件：

```env
MYSQL_ROOT_PASSWORD=your_root_password
MYSQL_DATABASE=subsidy
MYSQL_USER=subsidy_user
MYSQL_PASSWORD=your_db_password
REDIS_PASSWORD=your_redis_password
```

#### ② 构建前端静态资源

```bash
# 管理后台
cd frontend-admin
npm install && npm run build

# H5 端
cd ../frontend-h5
npm install && npm run build:h5
```

#### ③ 准备 SSL 证书

将 SSL 证书放置于 `ssl/` 目录：

- `ssl/cert.pem` — 证书文件
- `ssl/key.pem` — 私钥文件

如果不需要 HTTPS，可修改 `nginx/nginx.conf` 去除 SSL 相关配置，仅保留 80 端口。

#### ④ 启动服务

```bash
docker compose up -d --build
```

#### ⑤ 初始化数据库

```bash
# 进入后端容器执行迁移
docker compose exec backend alembic upgrade head

# 初始化种子数据
docker compose exec backend python scripts/seed_rbac.py
```

#### ⑥ 验证部署

- 管理后台：`https://your-domain.com/admin`
- H5 端：`https://your-domain.com/h5`
- API 健康检查：`https://your-domain.com/api/health`

### 6.3 Nginx 配置说明

Nginx 配置文件位于 [nginx/nginx.conf](nginx/nginx.conf)，包含以下配置：

- **HTTP → HTTPS 重定向**：80 端口自动跳转 443
- **安全头**：HSTS、X-Frame-Options、X-Content-Type-Options
- **静态资源**：`/admin` 和 `/h5` 路径分别指向管理端和 H5 构建产物
- **API 代理**：`/api/` 路径代理到后端 `8000` 端口
- **WebSocket 代理**：`/ws/` 路径代理到后端，支持协议升级

---

## 7. 项目结构

```
code/
├── backend/                        # 后端服务（FastAPI）
│   ├── alembic/                    # 数据库迁移
│   │   ├── versions/               # 迁移版本文件
│   │   └── env.py                  # 迁移环境配置
│   ├── app/
│   │   ├── api/                    # API 路由
│   │   │   ├── v1/                 # REST API v1
│   │   │   │   ├── auth/           # 认证接口（admin / h5 / 通用）
│   │   │   │   └── system/         # 系统管理接口（用户/角色/部门/菜单/H5用户）
│   │   │   └── ws/                 # WebSocket 端点（admin / h5）
│   │   ├── core/                   # 核心配置
│   │   │   ├── config.py           # 环境变量配置
│   │   │   ├── database.py         # 数据库连接与 Session
│   │   │   ├── security.py         # JWT / 密码 / 权限守卫
│   │   │   ├── error_handler.py    # 全局异常处理
│   │   │   └── exceptions.py       # 自定义异常类
│   │   ├── models/                 # 数据模型（ORM）
│   │   │   ├── base.py             # 基础模型（TimestampMixin）
│   │   │   ├── user.py             # 管理端用户模型
│   │   │   ├── h5_user.py          # H5端用户模型（含敏感信息字段）
│   │   │   ├── role.py             # 角色模型
│   │   │   ├── department.py       # 部门模型
│   │   │   └── menu.py             # 菜单模型
│   │   ├── schemas/                # Pydantic 数据校验
│   │   ├── services/               # 业务逻辑层
│   │   │   ├── auth_service.py     # 认证服务
│   │   │   ├── rbac_service.py     # RBAC 服务
│   │   │   ├── user_service.py     # 用户服务
│   │   │   └── online_service.py   # 在线统计服务
│   │   ├── tasks/                  # 后台任务
│   │   │   └── cleanup.py          # 心跳清理任务
│   │   └── utils/                  # 工具类
│   │       ├── redis.py            # Redis 连接管理
│   │       └── error_logger.py     # 错误日志
│   ├── scripts/
│   │   └── seed_rbac.py            # 种子数据初始化
│   ├── main.py                     # 应用入口
│   ├── requirements.txt            # Python 依赖
│   ├── Dockerfile                  # 后端容器镜像
│   └── alembic.ini                 # Alembic 配置
│
├── frontend-admin/                 # 管理后台（Vue3 + Element Plus）
│   ├── src/
│   │   ├── api/                    # API 接口封装
│   │   │   ├── request.ts          # Axios 实例 + 拦截器
│   │   │   └── modules/            # 按模块拆分（user / role / menu / department / admin）
│   │   ├── components/
│   │   │   ├── business/           # 业务组件（IconPicker / OnlineCounter）
│   │   │   └── layout/             # 布局组件（AdminLayout）
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts     # WebSocket 连接 Hook
│   │   ├── router/
│   │   │   └── index.ts            # 路由配置 + 守卫
│   │   ├── stores/
│   │   │   └── auth.ts             # 认证状态管理（Pinia）
│   │   ├── views/
│   │   │   ├── auth/               # 登录页
│   │   │   ├── dashboard/          # 首页仪表盘
│   │   │   └── system/             # 系统管理页面（部门/角色/用户/菜单/功能控制）
│   │   ├── assets/styles/          # 全局样式
│   │   ├── App.vue                 # 根组件
│   │   └── main.ts                 # 入口文件
│   ├── vite.config.ts              # Vite 配置
│   ├── tsconfig.json               # TypeScript 配置
│   ├── index.html                  # HTML 入口
│   └── package.json
│
├── frontend-h5/                    # H5 移动端（uni-app）
│   ├── src/
│   │   ├── api/                    # API 接口封装
│   │   │   ├── request.ts          # 请求实例
│   │   │   └── modules/auth.ts     # 认证接口
│   │   ├── hooks/
│   │   │   └── useWebSocket.ts     # WebSocket 连接 Hook
│   │   ├── pages/
│   │   │   ├── login/              # 登录页
│   │   │   └── operation/          # 业务操作页
│   │   ├── stores/
│   │   │   └── user.ts             # 用户状态管理
│   │   ├── styles/                 # 全局样式
│   │   ├── App.vue                 # 根组件
│   │   ├── main.ts                 # 入口文件
│   │   ├── pages.json              # 页面配置
│   │   └── manifest.json           # 应用配置
│   ├── vite.config.ts              # Vite 配置
│   └── package.json
│
├── nginx/
│   └── nginx.conf                  # Nginx 配置
├── docker-compose.yml              # 容器编排
└── .gitignore
```

---

## 8. 常见问题

### Q1：启动后端时提示数据库连接失败

**原因**：MySQL 服务未启动或 `.env` 中 `DATABASE_URL` 配置不正确。

**解决**：
1. 确认 MySQL 服务已启动
2. 检查 `.env` 中的数据库连接地址、用户名、密码是否正确
3. 确认数据库 `subsidy` 已创建

### Q2：Alembic 迁移报错

**原因**：数据库表结构与迁移版本不一致。

**解决**：
```bash
# 查看当前迁移版本
alembic current

# 查看迁移历史
alembic history

# 强制标记到最新版本（跳过迁移）
alembic stamp head
```

### Q3：登录失败提示"登录信息无效"

**原因**：种子数据未初始化或 Token 已过期。

**解决**：
1. 运行 `python scripts/seed_rbac.py` 初始化种子数据
2. 默认超级管理员账号：`admin / admin123456`
3. 如果 Token 过期，重新登录即可

### Q4：前端请求 API 报 404

**原因**：Vite 代理未正确配置。

**解决**：确保 `frontend-admin/vite.config.ts` 中的代理配置正确，后端服务已启动在 `8000` 端口。

### Q5：WebSocket 连接失败

**原因**：`ENABLE_WEBSOCKET` 配置为 `false` 或 Redis 未连接。

**解决**：
1. 检查 `.env` 中 `ENABLE_WEBSOCKET=true`
2. 确认 Redis 服务已启动
3. 检查 `REDIS_URL` 配置是否正确

### Q6：Docker 部署后 Nginx 返回 502

**原因**：后端容器未启动成功或 Nginx 无法解析 `backend` 服务名。

**解决**：
```bash
# 查看容器状态
docker compose ps

# 查看后端日志
docker compose logs backend

# 重启所有服务
docker compose restart
```

### Q7：前端页面刷新后白屏或 404

**原因**：Nginx 未配置 SPA 路由回退或 `base` 路径配置不一致。

**解决**：确认 `nginx/nginx.conf` 中 `try_files` 配置正确，`vite.config.ts` 中 `base` 路径与 Nginx 的 `location` 路径一致。

---
