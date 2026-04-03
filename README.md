# Dungeon Toolkit

> 面向中文 D&D 玩家的开源工具箱 —— 向导式角色创建 · 角色卡管理

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![React](https://img.shields.io/badge/React-19-61dafb)

## 项目简介

Dungeon Toolkit 是一个面向中文 D&D 玩家的开源工具箱
> 本项目代码主要由 AI 辅助生成，可能存在错漏或不完善之处，欢迎提 Issue 和 PR。

### 前端优化说明（2026-03）

- 机器人广场搜索已使用防抖策略，避免每次按键都触发请求。
- API 401 处理采用 refresh-first 流程：优先刷新 access token，失败后再清理登录态并跳转登录页。
- 路由采用懒加载与统一加载占位，降低首屏加载压力。
- `/robots/my` 已合并到 `/profile`，旧地址会自动重定向。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 19 + TypeScript + Vite + Tailwind CSS |
| 后端 | Django 4 + Django REST Framework + SimpleJWT |
| 数据库 | PostgreSQL 15 |
| 容器化 | Docker + Docker Compose |
| 部署 | Nginx + Gunicorn + 腾讯云 CVM |

---

## 本地开发环境搭建

### 前置条件

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) （用于运行本地数据库）
- Python 3.11+
- Node.js 18+

### 1. 克隆项目

```bash
git clone https://github.com/pear-studio/dungeon-toolkit-web.git
cd dungeon-toolkit-web
```

### 2. 启动数据库

```bash
# 仅启动 PostgreSQL 容器
docker compose -f docker-compose.dev.yml up -d
```

### 3. 启动后端

```bash
cd backend

# 创建并激活虚拟环境
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（复制示例文件后可直接使用默认值）
copy backend\.env.example backend\.env

# 初始化数据库
python manage.py makemigrations
python manage.py migrate

# 启动开发服务器（默认 http://localhost:8000）
python manage.py runserver
```

### 4. 启动前端

```bash
# 新开一个终端
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认 http://localhost:5173）
npm run dev
```

### 5. 验证运行

打开浏览器访问 **http://localhost:5173**，应看到 Dungeon Toolkit 登录页面。

| 服务 | 地址 |
|------|------|
| 前端页面 | http://localhost:5173 |
| 后端 API | http://localhost:8000/api/ |
| 健康检查 | http://localhost:8000/api/health/ |

注册一个账户后即可登录进入冒险者大厅。

---

## 测试

### 运行测试

```bash
cd backend

# 激活虚拟环境
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 运行所有测试
pytest

# 运行带覆盖率报告
pytest --cov=. --cov-report=html
```

### 测试账号

项目提供了测试账号用于人工测试：

```bash
# 初始化固定测试夹具
python manage.py seed_test_data --profile baseline --strict

# 一键重置并校验（推荐）
bash scripts/dev.sh reset-test-data
bash scripts/dev.sh verify-test-data
```

| 用户名 | 密码 | 场景 |
|--------|------|------|
| fixture_normal | FixturePass1234 | 常规登录/点击验证 |
| fixture_expired | FixturePass1234 | access 过期恢复验证 |
| fixture_refresh_fail | FixturePass1234 | refresh 失败回退验证 |

详细测试说明请参阅 [docs/testing.md](docs/testing.md)。

### 一键开发脚本（Docker）

项目根目录提供 `scripts/dev.sh` 统一入口（建议在 WSL/bash 中执行）：

```bash
bash scripts/dev.sh start    # 启动开发环境
bash scripts/dev.sh test     # 后端 pytest + 前端 lint
bash scripts/dev.sh lint     # 前端 lint
bash scripts/dev.sh check    # test + lint
bash scripts/dev.sh rebuild  # 停止、重建、迁移
```

可选：启动 Web + Standalone Bot 联调环境（依赖相邻目录存在 `../nonebot-dicepp`）：

```bash
bash scripts/dev.sh dev-with-bot --bot-id 123456789
bash scripts/dev.sh logs-bot --tail 100 --follow
```

---

## WebSocket 网关（网页聊天）

### 端点

- 用户端：`/ws/chat/<bot_uuid>/?token=<access_token>`
- 机器人端：`/ws/bot/`

### 本地运行（ASGI）

后端 WebSocket 需要 ASGI 入口，本项目默认使用 `config.asgi:application`：

```bash
cd backend
uvicorn config.asgi:application --host 0.0.0.0 --port 8000 --reload
```

### 协议文档

完整协议（`ack` / `system` / `bot_message` / `user_message`）见 [docs/websocket-gateway.md](docs/websocket-gateway.md)。

### Mock Bot（独立测试）

```bash
cd backend
python scripts/mock_bot.py --base-url ws://localhost:8000 --api-key <BOT_API_KEY>
```

### WebSocket 网关测试

使用 pytest 运行 WebSocket 集成测试：

```bash
cd backend

# 运行所有 WebSocket 测试
pytest apps/bots/tests/test_websocket_gateway.py -v

# 运行特定测试类
pytest apps/bots/tests/test_websocket_gateway.py::TestBotGateway -v
pytest apps/bots/tests/test_websocket_gateway.py::TestUserGateway -v
pytest apps/bots/tests/test_websocket_gateway.py::TestMessageRelay -v
```

**测试覆盖场景**

- **TestBotGateway**: Bot 连接认证、无效 key 拒绝、消息接收
- **TestUserGateway**: JWT 认证、离线系统消息、ack 响应
- **TestMessageRelay**: 双向消息中继、断开通知
- **TestRateLimiting**: 频率限制

**测试特点**

- 使用内存 Channel Layer（`InMemoryChannelLayer`），无需外部服务
- 测试隔离，可并行运行
- 直接集成到 CI/CD 流程

### 验收前置条件（网页聊天）

1. 准备测试账号并登录（建议使用 `fixture_normal / FixturePass1234`）
2. 确认浏览器已存在 `access_token`（登录后自动写入）
3. 启动后端 ASGI 服务与前端页面，并确保 `/ws/` 可访问
4. （可选）启动 Mock Bot；若不启动，聊天页面应出现机器人离线提示且输入框禁用

### 验收步骤（登录态相关）

1. 未登录访问聊天：应显示“请先登录后再使用聊天”，输入框与发送按钮禁用
2. 登录后访问聊天：
   - WebSocket 通道连通且机器人在线时，输入框可用
   - 机器人离线时，显示离线提示且输入框禁用
3. 同一账号同一机器人打开第二个标签页时，旧标签页应收到提示并被断开

### 生产部署说明

- Nginx 需为 `/ws/` 配置 `Upgrade`/`Connection` 头并提升 `proxy_read_timeout`
- 当前 `CHANNEL_LAYERS` 使用 `InMemoryChannelLayer`，**仅支持单进程**
- 生产若继续使用 InMemory，ASGI worker 必须为 `1`
- 多 worker / 多实例场景需切换到 Redis Channel Layer

---

## 目录结构

```
dungeon-toolkit/
├── backend/          # Django 后端
│   ├── apps/         # 应用模块（users / bots）
│   ├── config/       # Django 配置
│   └── requirements.txt
├── frontend/         # React 前端
│   └── src/
│       ├── pages/    # 页面组件
│       ├── stores/   # Zustand 状态管理
│       └── lib/      # API 请求层
├── nginx/            # Nginx 配置（生产环境）
├── openspec/         # 项目设计文档
├── docker-compose.yml          # 生产环境
└── docker-compose.dev.yml      # 开发环境（仅数据库）
```

---

## License

[MIT](LICENSE)

---

## 文档索引

- 开发指南：`docs/development.md`
- 测试指南：`docs/testing.md`
- 部署指南：`docs/deployment.md`
- 命令速查：`docs/commands.md`
