# Dungeon Toolkit 开发命令集
# 用法: make <命令> 或 make help

.PHONY: help install dev build up down rebuild test lint check status logs

# ── 帮助 ──────────────────────────────────────────────────────────────────────
help:  ## 显示所有可用命令
	@echo "Dungeon Toolkit 命令集"
	@echo ""
	@echo "开发命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | \
		grep -v 'deploy\|prod' | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""
	@echo "生产部署:"
	@grep -E '^(deploy|build|up|down|logs):.*?## ' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-15s %s\n", $$1, $$2}'
	@echo ""
	@echo "提示: 所有开发命令底层调用 scripts/dev.sh"
	@echo "      生产命令底层调用 docker compose"

# ── 开发命令 (底层调用 scripts/dev.sh) ────────────────────────────────────────
install:  ## 安装依赖（容器内）
	@bash scripts/dev.sh rebuild

dev:  ## 启动开发环境
	@bash scripts/dev.sh start

dev-down:  ## 停止开发环境
	@bash scripts/dev.sh stop

dev-status:  ## 查看开发环境状态
	@bash scripts/dev.sh status

rebuild:  ## 重建开发环境（含迁移）
	@bash scripts/dev.sh rebuild

test:  ## 运行测试（后端 + 前端 lint）
	@bash scripts/dev.sh test

lint:  ## 代码检查
	@bash scripts/dev.sh lint

check:  ## 运行测试 + 代码检查
	@bash scripts/dev.sh check

restart-backend:  ## 重启后端服务
	@bash scripts/dev.sh restart-backend

restart-frontend:  ## 重启前端服务
	@bash scripts/dev.sh restart-frontend

seed:  ## 初始化测试数据
	@bash scripts/dev.sh seed-test-data

# ── 生产部署 (直接调用 docker compose) ────────────────────────────────────────
DC := docker compose

build:  ## 构建生产镜像
	$(DC) build

up:  ## 启动生产环境
	$(DC) up -d

down:  ## 停止生产环境
	$(DC) down

deps:  ## 查看生产服务状态
	$(DC) ps

logs:  ## 查看生产日志
	$(DC) logs -f

# ── 服务器初始化 ──────────────────────────────────────────────────────────────
setup-server:  ## 初始化 Ubuntu 服务器（安装 Docker、配置防火墙）
	@bash scripts/setup_server.sh
