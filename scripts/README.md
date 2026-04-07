# Scripts

本目录包含项目开发和部署所需的脚本。

## 📁 文件说明

| 脚本 | 平台 | 用途 |
|------|------|------|
| `dev.sh` | Linux/WSL | 统一开发脚本（底层命令） |
| `setup_server.sh` | Linux | 生产服务器初始化 |

> 推荐使用 **Makefile** 作为统一入口，详见项目根目录 `Makefile`。

---

## 🚀 快速开始（推荐）

项目根目录已提供 `Makefile`，所有常用命令一行搞定：

```bash
# 查看所有可用命令
make help

# 开发环境
make dev              # 启动开发环境
make rebuild          # 重建开发环境（含迁移）
make test             # 运行测试
make lint             # 代码检查
make check            # 测试 + 检查
make dev-down         # 停止开发环境

# 生产部署
make build            # 构建生产镜像
make up               # 启动生产环境
make down             # 停止生产环境
make logs             # 查看生产日志

# 服务器初始化
make setup-server     # 初始化 Ubuntu 服务器
```

---

## 🛠️ dev.sh - 统一开发脚本

如需直接使用底层脚本：

```bash
# 完整重建环境（停止容器、重新构建、迁移数据）
bash scripts/dev.sh rebuild

# 启动/停止/查看状态
bash scripts/dev.sh start
bash scripts/dev.sh stop
bash scripts/dev.sh status

# 运行测试 + 代码检查
bash scripts/dev.sh test
bash scripts/dev.sh lint
bash scripts/dev.sh check

# 只重启单个服务
bash scripts/dev.sh restart-frontend
bash scripts/dev.sh restart-backend

# 测试数据管理
bash scripts/dev.sh seed-test-data
bash scripts/dev.sh reset-test-data baseline
bash scripts/dev.sh verify-test-data

# Web + Bot 联调（--bot-id 必填）
bash scripts/dev.sh dev-with-bot --bot-id 123456789

# 查看帮助
bash scripts/dev.sh help
```

### 服务地址

- **前端**: http://localhost:5173
- **后端**: http://localhost:8000
- **数据库**: localhost:5432

---

## 🖥️ setup_server.sh - 生产服务器初始化

用于全新 Ubuntu 服务器的环境初始化：

```bash
# 以 root 权限执行
bash scripts/setup_server.sh
```

执行内容：
1. 更新系统包
2. 安装 Docker 和 Docker Compose
3. 安装常用工具（git, curl, vim, ufw）
4. 配置防火墙（开放 22, 80, 443 端口）

---

## 📝 注意事项

1. 所有脚本需在 **Linux 或 WSL** 环境下执行
2. 开发脚本依赖 Docker 和 Docker Compose
3. 首次运行 `make rebuild` 会自动创建数据库并执行迁移
