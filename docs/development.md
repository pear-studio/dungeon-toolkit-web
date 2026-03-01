# 开发环境设置

> **推荐方式**: 完全在 Docker 中运行开发环境，无需在本地安装 Python、Node.js 等工具

---

## 前置要求

### 1. 安装/升级 Docker

如果还没有安装 Docker，或需要升级到最新版本：

```bash
# 安装 Docker（Ubuntu/Debian）
sudo apt update
sudo apt install docker.io

# 启动 Docker 服务
sudo systemctl start docker
sudo systemctl enable docker

# 将当前用户加入 docker 组（可选，避免每次加 sudo）
sudo usermod -aG docker $USER

# 重新登录后生效，或执行以下命令立即生效
newgrp docker

# 验证 Docker 版本
docker --version
```

### 2. 安装 Docker Compose v2

```bash
# 下载 Docker Compose v2
sudo curl -L "https://ghfast.top/https://github.com/docker/compose/releases/download/v2.24.6/docker-compose-linux-x86_64" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 刷新 PATH 缓存
hash -r

# 验证版本（应该是 v2.24.6）
docker-compose --version
```

> **注意**: 如果 `docker-compose`（v2 子命令）不可用，但 `docker-compose --version` 显示 v2.x，可以使用 `docker-compose` 代替 `docker compose`（将所有命令中的空格改为连字符）。

---

## 方式一：Docker 中运行开发环境（推荐）

### 前置要求

- WSL2 中安装好 Docker
- Docker Compose v2

### 快速启动

```bash
# 1. 构建并启动所有服务（首次约需 3-5 分钟）
docker-compose -f docker-compose.dev.yml up -d --build

# 2. 查看服务状态
docker-compose -f docker-compose.dev.yml ps

# 3. 查看日志
docker-compose -f docker-compose.dev.yml logs -f
```

### 访问服务

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端 | http://localhost:5173 | React 开发服务器 (热重载) |
| 后端 | http://localhost:8000 | Django 开发服务器 (热重载) |
| 数据库 | localhost:5432 | PostgreSQL |

### 代码修改

- **后端**: 修改 `backend/` 目录下的代码，会自动热重载
- **前端**: 修改 `frontend/` 目录下的代码，会自动热重载

### 常用命令

```bash
# 重新构建（代码有更新时）
docker compose -f docker-compose.dev.yml up -d --build

# 停止服务
docker compose -f docker-compose.dev.yml down

# 查看后端日志
docker compose -f docker-compose.dev.yml logs -f backend

# 查看前端日志
docker compose -f docker-compose.dev.yml logs -f frontend

# 进入后端容器（调试用）
docker compose -f docker-compose.dev.yml exec backend bash

# 进入前端容器（调试用）
docker compose -f docker-compose.dev.yml exec frontend sh

# 运行测试
docker compose -f docker-compose.dev.yml exec backend pytest
```

### 初始化数据库

```bash
# 迁移数据库
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate

# 创建测试用户
docker compose -f docker-compose.dev.yml exec backend python manage.py create_test_users

# 导入游戏数据（可选）
docker compose -f docker-compose.dev.yml exec backend python scripts/import_gamedata.py
```

### 使用开发脚本

项目提供了统一的开发脚本，简化常用操作：

```bash
# 进入项目目录（WSL Ubuntu）
cd /mnt/c/Workspace/dungeon-toolkit-web  # 或 cd ~/dungeon-toolkit-web

# 重建开发环境（停止、重新构建、迁移数据）
bash scripts/dev.sh rebuild

# 启动开发环境
bash scripts/dev.sh start

# 停止开发环境
bash scripts/dev.sh stop

# 查看环境状态
bash scripts/dev.sh status

# 运行测试
bash scripts/dev.sh test

# 运行代码检查
bash scripts/dev.sh lint

# 完整检查（测试 + lint）
bash scripts/dev.sh check
```

---

## 方式二：本地运行（不推荐）

如果需要本地运行（不通过 Docker），请参考以下步骤：

### 1. 启动 Docker 数据库

```bash
docker-compose -f docker-compose.dev.yml up -d db
```

### 2. 安装依赖

**后端 (Python 3.12)**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**前端 (Node.js 20)**:
```bash
cd frontend
npm install
```

### 3. 运行服务

```bash
# 后端
cd backend
python manage.py migrate
python manage.py runserver

# 前端
cd frontend
npm run dev
```

---

## 测试环境

测试环境使用独立的数据库和服务：

```bash
# 启动测试环境
docker compose -f docker-compose.test.yml up -d --build

# 运行测试
docker compose -f docker-compose.test.yml exec backend-test pytest
```

---

## 环境变量

### 开发环境 (docker-compose.dev.yml)

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `DB_HOST` | db | 数据库主机 |
| `DB_PORT` | 5432 | 数据库端口 |
| `DB_NAME` | dungeon_toolkit | 数据库名 |
| `DB_USER` | dungeon_toolkit | 数据库用户 |
| `DB_PASSWORD` | dungeon_toolkit | 数据库密码 |
| `VITE_API_BASE_URL` | http://backend:8000 | 前端 API 代理目标 |

---

## 常见问题

### 前端无法连接后端

确保 `VITE_API_BASE_URL` 环境变量设置为 `http://backend:8000`（Docker 内部网络）。

### 数据库连接失败

检查数据库是否启动：
```bash
docker compose -f docker-compose.dev.yml ps db
```

### 端口被占用

修改 `docker-compose.dev.yml` 中的端口映射：
```yaml
ports:
  - "8001:8000"  # 后端
  - "5174:5173"  # 前端
```
