#!/bin/bash
# ============================================================
# dev.sh - 统一开发脚本
# 用法（在 WSL Ubuntu 中执行）：
#   bash scripts/dev.sh rebuild     # 重建环境（停止容器、重新构建、迁移数据）
#   bash scripts/dev.sh test        # 运行测试
#   bash scripts/dev.sh lint        # 代码检查
#   bash scripts/dev.sh check       # 运行测试 + 代码检查
#   bash scripts/dev.sh start       # 启动开发环境
#   bash scripts/dev.sh stop        # 停止开发环境
#   bash scripts/dev.sh status      # 查看环境状态
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

COMMAND="${1:-help}"

if command -v docker &>/dev/null && docker compose version &>/dev/null 2>&1; then
  DC="docker compose"
elif command -v docker-compose &>/dev/null; then
  DC="docker-compose"
else
  echo "❌ 未找到可用的 docker / docker compose 命令"
  exit 1
fi

echo "📁 工作目录: $PROJECT_ROOT"
echo "  ✓ 使用: $DC"

start_dev() {
  echo ""
  echo "▶ 启动开发环境..."
  $DC -f docker-compose.dev.yml up -d
  echo ""
  echo "  ✓ 开发环境已启动"
  echo ""
  echo "  服务地址："
  echo "    前端: http://localhost:5173"
  echo "    后端: http://localhost:8000"
  echo "    数据库: localhost:5432"
}

stop_dev() {
  echo ""
  echo "▶ 停止开发环境..."
  $DC -f docker-compose.dev.yml down
  echo "  ✓ 已停止"
}

status_dev() {
  echo ""
  echo "▶ 环境状态..."
  $DC -f docker-compose.dev.yml ps
}

rebuild_dev() {
  echo ""
  echo "▶ [1/4] 停止并重建容器..."
  $DC -f docker-compose.dev.yml down
  $DC -f docker-compose.dev.yml up -d --build

  echo ""
  echo "▶ [2/4] 等待数据库就绪..."
  sleep 5
  RETRY=0
  MAX_RETRY=30
  until docker exec dungeon-toolkit-web-db-1 pg_isready -U "${POSTGRES_USER:-dungeon_toolkit}" > /dev/null 2>&1; do
    RETRY=$((RETRY + 1))
    if [ $RETRY -ge $MAX_RETRY ]; then
      echo "❌ 数据库超时"
      exit 1
    fi
    printf "  等待中... (%d/%d)\n" $RETRY $MAX_RETRY
    sleep 2
  done
  echo "  ✓ 数据库已就绪"

  echo ""
  echo "▶ [3/4] 应用迁移..."
  $DC exec -T backend python manage.py migrate
  echo "  ✓ 迁移完成"

  echo ""
  echo "🎉 重建完成！"
  echo ""
  echo "  访问："
  echo "    前端: http://localhost:5173"
  echo "    后端: http://localhost:8000"
}

run_tests() {
  echo ""
  echo "▶ 运行测试..."
  echo "========================================"

  $DC exec -T backend pytest -v --tb=short
  $DC exec -T frontend npm run lint

  echo ""
  echo "🎉 测试通过！"
}

run_lint() {
  echo ""
  echo "▶ 代码检查..."
  echo "========================================"

  $DC exec -T frontend npm run lint

  echo ""
  echo "🎉 代码检查通过！"
}

run_check() {
  run_tests
  run_lint
}

show_help() {
  echo "用法: $0 <命令>"
  echo ""
  echo "命令:"
  echo "  rebuild  重建开发环境（停止、构建、迁移、导入数据）"
  echo "  start    启动开发环境"
  echo "  stop     停止开发环境"
  echo "  status   查看环境状态"
  echo "  test     运行测试"
  echo "  lint     代码检查"
  echo "  check    运行测试 + 代码检查"
  echo "  help     显示帮助"
  echo ""
  echo "示例:"
  echo "  bash scripts/dev.sh rebuild"
  echo "  bash scripts/dev.sh test"
  echo "  bash scripts/dev.sh check"
}

case "$COMMAND" in
  rebuild)
    rebuild_dev
    ;;
  start)
    start_dev
    ;;
  stop)
    stop_dev
    ;;
  status)
    status_dev
    ;;
  test)
    run_tests
    ;;
  lint)
    run_lint
    ;;
  check)
    run_check
    ;;
  help|--help|-h|"")
    show_help
    ;;
  *)
    echo "未知命令: $COMMAND"
    echo ""
    show_help
    exit 1
    ;;
esac
