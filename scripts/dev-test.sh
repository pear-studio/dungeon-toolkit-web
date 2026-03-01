#!/bin/bash
# ============================================================
# dev-test.sh - 本地开发环境测试脚本
# 用法（在 WSL Ubuntu 中执行）：
#   bash scripts/dev-test.sh              # 运行所有测试
#   bash scripts/dev-test.sh --backend    # 只运行后端测试
#   bash scripts/dev-test.sh --frontend    # 只运行前端测试
#   bash scripts/dev-test.sh --lint        # 只运行代码检查
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

MODE="${1:-all}"

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

check_db() {
  if ! $DC ps --format json 2>/dev/null | grep -q "db"; then
    echo "❌ 数据库容器未运行，请先运行: docker-compose -f docker-compose.dev.yml up -d"
    exit 1
  fi
}

run_backend_tests() {
  echo ""
  echo "▶ 运行后端测试..."
  echo "========================================"

  if ! $DC exec -T backend python -c "import pytest" &>/dev/null; then
    echo "❌ 后端容器未运行，先执行: docker-compose -f docker-compose.dev.yml up -d"
    exit 1
  fi

  $DC exec -T backend pytest -v --tb=short
  echo "  ✓ 后端测试完成"
}

run_frontend_tests() {
  echo ""
  echo "▶ 运行前端检查..."
  echo "========================================"

  if ! $DC exec -T frontend npm list &>/dev/null; then
    echo "❌ 前端容器未运行，先执行: docker-compose -f docker-compose.dev.yml up -d"
    exit 1
  fi

  $DC exec -T frontend npm run lint
  echo "  ✓ 前端检查完成"
}

run_all() {
  run_backend_tests
  run_frontend_tests
  echo ""
  echo "🎉 所有测试通过！"
}

case "$MODE" in
  --backend|-b)
    check_db
    run_backend_tests
    ;;
  --frontend|-f)
    run_frontend_tests
    ;;
  --lint|-l)
    run_frontend_tests
    ;;
  --all|-a|"")
    check_db
    run_all
    ;;
  *)
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --backend, -b    只运行后端测试"
    echo "  --frontend, -f   只运行前端代码检查"
    echo "  --lint, -l       同 --frontend"
    echo "  --all, -a        运行所有测试（默认）"
    exit 1
    ;;
esac
