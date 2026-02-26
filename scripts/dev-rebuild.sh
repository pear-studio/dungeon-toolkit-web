#!/bin/bash
# ============================================================
# dev-rebuild.sh - 本地开发环境一键重建脚本
# 用法（在 WSL 中执行）：
#   bash scripts/dev-rebuild.sh
# ============================================================

set -e  # 任意步骤失败即退出

# ── 切换到项目根目录 ───────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"
echo "📁 工作目录: $PROJECT_ROOT"

# ── 检测 docker compose 命令 ──────────────────────────────
# 优先使用原生 docker-ce（WSL 直装），其次兼容 Docker Desktop
if command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
  DC="docker compose"
  echo "  ✓ 使用: docker compose ($(docker compose version --short 2>/dev/null || echo 'v2'))"
elif command -v docker-compose &>/dev/null; then
  DC="docker-compose"
  echo "  ✓ 使用: docker-compose (v1 legacy)"
else
  echo "❌ 未找到可用的 docker / docker compose 命令"
  echo "   → WSL 原生 docker: sudo apt install docker.io docker-compose-v2"
  echo "   → 若 docker 存在但无权限: sudo usermod -aG docker \$USER && newgrp docker"
  exit 1
fi

# ── 检测 docker daemon 是否运行 ───────────────────────────
if ! docker info &>/dev/null 2>&1; then
  echo "❌ Docker daemon 未运行"
  echo "   → 启动方式: sudo service docker start"
  echo "   → 或: sudo dockerd &"
  exit 1
fi
echo "  ✓ Docker daemon 运行中"

# ── 1. 停止并重建镜像 ──────────────────────────────────────
echo ""
echo "▶ [1/4] 停止旧容器并重建镜像..."
$DC down
$DC up -d --build
echo "  ✓ 容器启动完成"

# ── 2. 等待数据库就绪 ─────────────────────────────────────
echo ""
echo "▶ [2/4] 等待数据库就绪..."
RETRY=0
MAX_RETRY=30
until $DC exec -T db pg_isready -U "${POSTGRES_USER:-dndchar}" > /dev/null 2>&1; do
  RETRY=$((RETRY + 1))
  if [ $RETRY -ge $MAX_RETRY ]; then
    echo "❌ 数据库超时，请检查容器日志：$DC logs db"
    exit 1
  fi
  printf "  等待中... (%d/%d)\n" $RETRY $MAX_RETRY
  sleep 2
done
echo "  ✓ 数据库已就绪"

# ── 3. 应用迁移 ────────────────────────────────────────────
echo ""
echo "▶ [3/4] 应用数据库迁移..."
$DC exec -T backend python manage.py migrate
echo "  ✓ 迁移完成"

# ── 4. 导入游戏数据 ────────────────────────────────────────
echo ""
echo "▶ [4/4] 导入游戏数据..."
$DC exec -T backend python scripts/import_gamedata.py
echo "  ✓ 数据导入完成"

# ── 完成 ───────────────────────────────────────────────────
echo ""
echo "🎉 重建完成！后端已就绪"
echo ""
echo "   验证 API：  python3 unittest/test_api.py"
echo "   查看日志：  $DC logs -f backend"
echo "   进入容器：  $DC exec backend bash"