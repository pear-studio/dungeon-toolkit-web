# Scripts

本目录包含项目开发和部署所需的脚本。

## 📁 文件说明

| 脚本 | 平台 | 用途 |
|------|------|------|
| `dev.sh` | Linux/WSL | 统一开发脚本（推荐） |
| `dev-rebuild.sh` | Linux/WSL | 快速重建开发环境 |
| `dev-test.sh` | Linux/WSL | 运行测试 |
| `dev-lint.sh` | Linux/WSL | 代码检查 |
| `setup_server.sh` | Linux | 生产服务器初始化 |

---

## 🚀 dev.sh - 统一开发脚本

这是主要的开发脚本，整合了所有开发相关命令。

### 使用方法

在 WSL Ubuntu 中执行：

```bash
# 完整重建环境（停止容器、重新构建、迁移数据）
bash scripts/dev.sh rebuild

# 启动/停止/查看状态
bash scripts/dev.sh start
bash scripts/dev.sh stop
bash scripts/dev.sh status

# 运行测试
bash scripts/dev.sh test

# 代码检查
bash scripts/dev.sh lint

# 运行测试 + 代码检查
bash scripts/dev.sh check

# 只重启前端服务（修改网页布局时使用）
bash scripts/dev.sh restart-frontend

# 只重启后端服务（修改后端代码时使用）
bash scripts/dev.sh restart-backend

# 查看帮助
bash scripts/dev.sh help
```

### 服务地址

启动后可访问：
- **前端**: http://localhost:5173
- **后端**: http://localhost:8000
- **数据库**: localhost:5432

---

## 🔧 快捷脚本

这些脚本是 `dev.sh` 对应命令的快捷方式：

```bash
# 等同于 dev.sh rebuild
bash scripts/dev-rebuild.sh

# 等同于 dev.sh test
bash scripts/dev-test.sh

# 等同于 dev.sh lint
bash scripts/dev-lint.sh
```

---

## 🖥️ setup_server.sh - 生产服务器初始化

用于在全新的 Ubuntu 服务器上初始化环境。

### 使用方法

```bash
# 以 root 权限执行
bash setup_server.sh
```

### 执行内容

1. 更新系统包
2. 安装 Docker 和 Docker Compose
3. 安装常用工具（git, curl, vim, ufw）
4. 配置防火墙（开放 22, 80, 443 端口）

### 后续步骤

脚本执行完成后，按照提示进行：

```bash
# 1. 拉取代码
git clone <your-repo-url> /app/dungeon-toolkit

# 2. 进入目录
cd /app/dungeon-toolkit

# 3. 配置环境变量
cp .env.example .env && vim .env

# 4. 启动服务
docker compose up -d --build

# 5. 访问网站
http://<your-server-ip>
```

---

## 📝 注意事项

1. 所有 `.sh` 脚本需要在 **Linux 或 WSL** 环境下执行
2. 开发脚本依赖 Docker 和 Docker Compose
3. 首次运行 `dev.sh rebuild` 会自动创建数据库并执行迁移