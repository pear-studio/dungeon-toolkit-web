#!/bin/bash
# =============================================================
# Dungeon Toolkit 服务器初始化脚本
# 适用于 Ubuntu 22.04 / 24.04
# 使用方法：bash setup_server.sh
# =============================================================

set -e  # 任意命令失败则退出

echo ""
echo "============================================"
echo "  Dungeon Toolkit 服务器初始化"
echo "============================================"
echo ""

# 更新系统
echo "[1/4] 更新系统包..."
apt-get update -qq
apt-get upgrade -y -qq

# 安装 Docker
echo "[2/4] 安装 Docker..."
if command -v docker &> /dev/null; then
    echo "  Docker 已安装，跳过"
else
    curl -fsSL https://get.docker.com | sh
    systemctl enable docker
    systemctl start docker
    echo "  Docker 安装完成"
fi

# 安装常用工具
echo "[3/4] 安装常用工具..."
apt-get install -y -qq git curl vim ufw

# 配置防火墙
echo "[4/4] 配置防火墙..."
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw --force enable

echo ""
echo "============================================"
echo "  初始化完成！Docker 版本："
docker --version
docker compose version
echo ""
echo "  接下来的步骤："
echo "  1. 拉取代码：git clone <your-repo-url> /app/dungeon-toolkit"
echo "  2. 进入目录：cd /app/dungeon-toolkit"
echo "  3. 配置环境：cp .env.example .env && vim .env"
echo "  4. 启动服务：docker compose up -d --build"
echo "  5. 访问网站：http://<your-server-ip>"
echo "============================================"
echo ""
