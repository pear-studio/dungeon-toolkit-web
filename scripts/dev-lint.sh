#!/bin/bash
# ============================================================
# dev-lint.sh - 本地代码检查脚本
# 用法（在 WSL Ubuntu 中执行）：
#   bash scripts/dev-lint.sh              # 检查所有
#   bash scripts/dev-lint.sh --backend    # 只检查后端
#   bash scripts/dev-lint.sh --frontend   # 只检查前端
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

check_backend_lint() {
  echo ""
  echo "▶ 检查后端代码..."
  echo "========================================"

  if ! $DC exec -T backend python -c "import ruff" &>/dev/null; then
    echo "  ⚠ ruff 未安装，跳过后端检查"
    return 0
  fi

  $DC exec -T backend ruff check .
  echo "  ✓ 后端检查完成"
}

check_frontend_lint() {
  echo ""
  echo "▶ 检查前端代码..."
  echo "========================================"

  if ! $DC exec -T frontend npm list &>/dev/null; then
    echo "❌ 前端容器未运行"
    exit 1
  fi

  $DC exec -T frontend npm run lint
  echo "  ✓ 前端检查完成"
}

check_frontend_types() {
  echo ""
  echo "▶ 检查前端类型..."
  echo "========================================"

  $DC exec -T frontend npx tsc --noEmit
  echo "  ✓ 前端类型检查完成"
}

run_all() {
  check_backend_lint
  check_frontend_lint
  check_frontend_types
  echo ""
  echo "🎉 所有代码检查通过！"
}

case "$MODE" in
  --backend|-b)
    check_backend_lint
    ;;
  --frontend|-f)
    check_frontend_lint
    ;;
  --types|-t)
    check_frontend_types
    ;;
  --all|-a|"")
    run_all
    ;;
  *)
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  --backend, -b   只检查后端代码"
    echo "  --frontend, -f 只检查前端 lint"
    echo "  --types, -t    只检查前端类型"
    echo "  --all, -a      检查所有（默认）"
    exit 1
    ;;
esac
