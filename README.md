# ⚔️ Dungeon Toolkit

> 面向中文 D&D 5e 玩家的开源工具箱 —— 向导式角色创建 · 角色卡管理

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![React](https://img.shields.io/badge/React-18-61dafb)

## 项目简介

Dungeon Toolkit 是一个面向中文 D&D 5e 玩家的开源工具箱，计划提供：

- 🧙 **向导式角色创建** — 8 步引导完成种族/职业/属性/背景全流程
- 📋 **角色卡管理** — 查看与编辑你的角色，支持公开分享

**当前进度：** Phase 1 MVP 开发中（用户注册/登录 + 基础框架已完成）

> ⚠️ **免责声明**：本项目代码主要由 AI 辅助生成，可能存在错漏或不完善之处，欢迎提 Issue 和 PR。

---

## 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18 + TypeScript + Vite + Tailwind CSS |
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
docker-compose -f docker-compose.dev.yml up -d
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
# 创建测试账号
python manage.py create_test_users
```

| 用户名 | 密码 | 角色 |
|--------|------|------|
| testuser | TestPass1234 | 普通用户 |
| admin | AdminPass1234 | 管理员 |
| runner | RunnerPass1234 | CI/CD |

详细测试说明请参阅 [docs/testing.md](docs/testing.md)。

---

## 目录结构

```
dungeon-toolkit/
├── backend/          # Django 后端
│   ├── apps/         # 应用模块（users / characters / gamedata 等）
│   ├── config/       # Django 配置
│   └── requirements.txt
├── frontend/         # React 前端
│   └── src/
│       ├── pages/    # 页面组件
│       ├── stores/   # Zustand 状态管理
│       └── api/      # Axios 请求层
├── nginx/            # Nginx 配置（生产环境）
├── openspec/         # 项目设计文档
├── docker-compose.yml          # 生产环境
└── docker-compose.dev.yml      # 开发环境（仅数据库）
```

---

## 开发状态

- [x] 用户注册 / 登录（JWT）
- [x] Dashboard 欢迎页
- [ ] 向导式角色创建（开发中）
- [ ] 角色卡管理

---

## License

[MIT](LICENSE)
