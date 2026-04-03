#!/bin/bash
# ============================================================
# dev.sh - 统一开发脚本
# 用法（在 WSL Ubuntu 中执行）：
#   bash scripts/dev.sh rebuild           # 重建环境（停止容器、重新构建、迁移）
#   bash scripts/dev.sh test              # 运行测试
#   bash scripts/dev.sh lint              # 代码检查
#   bash scripts/dev.sh check             # 运行测试 + 代码检查
#   bash scripts/dev.sh start             # 启动开发环境
#   bash scripts/dev.sh stop              # 停止开发环境
#   bash scripts/dev.sh status            # 查看环境状态
#   bash scripts/dev.sh restart-frontend  # 只重启前端服务（修改网页布局时使用）
#   bash scripts/dev.sh restart-backend   # 只重启后端服务（修改后端代码时使用）
#   bash scripts/dev.sh seed-test-data    # 初始化测试夹具数据
#   bash scripts/dev.sh reset-test-data   # 重置测试夹具数据
#   bash scripts/dev.sh verify-test-data  # 校验测试夹具完整性
# ============================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

if [ -f backend/.env ]; then
  set -a
  source backend/.env
  set +a
fi

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
  echo "    前端: http://\$(wsl hostname -I | awk '{print \$1}'):5173  (WSL2 IP, localhost:5173 在该环境下经常因 wslrelay 损坏无法访问)"
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
  echo "    前端: http://\$(wsl hostname -I | awk '{print \$1}'):5173  (WSL2 IP, localhost:5173 在该环境下经常因 wslrelay 损坏无法访问)"
  echo "    后端: http://localhost:8000"
}

run_tests() {
  echo ""
  echo "▶ 运行测试与前端检查..."
  echo "========================================"

  $DC exec -T backend pytest -v --tb=short
  $DC exec -T frontend npm run lint

  echo ""
  echo "🎉 测试与前端检查通过！"
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

restart_frontend() {
  echo ""
  echo "▶ 重启前端服务..."
  $DC -f docker-compose.dev.yml restart frontend
  echo "  ✓ 前端已重启"
  echo ""
  echo "  访问：前端: http://\$(wsl hostname -I | awk '{print \$1}'):5173  (WSL2 IP, localhost:5173 在此环境下经常因 wslrelay 损坏无法访问)"
}

restart_backend() {
  echo ""
  echo "▶ 重启后端服务..."
  $DC -f docker-compose.dev.yml restart backend
  echo "  ✓ 后端已重启"
  echo ""
  echo "  访问：后端：http://localhost:8000"
}

print_bot_failure_diagnostics() {
  echo ""
  echo "⚠ Bot 健康检查失败诊断信息："
  echo "  - BOT_ID: ${BOT_ID}"
  echo "  - HUB_URL: ${HUB_URL}"
  echo "  - 运行状态："
  $DC -f docker-compose.dev.yml --profile bot ps
  echo ""
  echo "  - Bot 最近日志（20行）："
  $DC -f docker-compose.dev.yml --profile bot logs --tail 20 bot || true
  echo ""
  echo "  - 提示：请确认 BOT_ID 未与测试夹具 ID (880001-880005) 冲突"
}

wait_backend_health() {
  local timeout_secs="${1:-60}"
  local retry=0
  local max_retry=$((timeout_secs / 2))
  if [ "$max_retry" -lt 1 ]; then
    max_retry=1
  fi

  echo ""
  echo "▶ 等待后端健康检查..."
  until curl -fsS "http://localhost:8000/api/health/" > /dev/null 2>&1; do
    retry=$((retry + 1))
    if [ "$retry" -ge "$max_retry" ]; then
      echo "❌ 后端健康检查超时"
      return 1
    fi
    printf "  等待中... (%d/%d)\n" "$retry" "$max_retry"
    sleep 2
  done
  echo "  ✓ 后端已就绪"
}

wait_bot_container_healthy() {
  local timeout_secs="${1:-60}"
  local retry=0
  local max_retry=$((timeout_secs / 2))
  local container_id=""
  local health_status=""
  if [ "$max_retry" -lt 1 ]; then
    max_retry=1
  fi

  echo ""
  echo "▶ 等待 Bot 容器健康状态..."
  container_id="$($DC -f docker-compose.dev.yml --profile bot ps -q bot)"
  if [ -z "$container_id" ]; then
    echo "❌ 未找到 Bot 容器"
    return 1
  fi

  while true; do
    health_status="$(docker inspect --format '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$container_id" 2>/dev/null || echo "unknown")"
    if [ "$health_status" = "healthy" ]; then
      echo "  ✓ Bot 容器健康检查通过"
      return 0
    fi
    retry=$((retry + 1))
    if [ "$retry" -ge "$max_retry" ]; then
      echo "❌ Bot 容器健康检查超时（当前状态: ${health_status}）"
      return 1
    fi
    printf "  等待中... (%d/%d), 状态=%s\n" "$retry" "$max_retry" "$health_status"
    sleep 2
  done
}

wait_bot_registered_online() {
  local timeout_secs="${1:-60}"
  local retry=0
  local max_retry=$((timeout_secs / 2))
  local page=1
  local response=""
  local parse_result=""
  local found="0"
  if [ "$max_retry" -lt 1 ]; then
    max_retry=1
  fi

  echo ""
  echo "▶ 等待 Bot 注册并在线 (BOT_ID=${BOT_ID})..."
  while [ "$retry" -lt "$max_retry" ]; do
    page=1
    found="0"

    while true; do
      response="$(curl -fsS "http://localhost:8000/api/bots/?page=${page}" 2>/dev/null || true)"
      if [ -z "$response" ]; then
        break
      fi

      parse_result="$(API_JSON="$response" python3 - "$BOT_ID" <<'PY'
import json
import os
import sys

bot_id = sys.argv[1]
payload = json.loads(os.environ["API_JSON"])
for bot in payload.get("results", []):
    if str(bot.get("bot_id")) == bot_id:
        status = str(bot.get("status", ""))
        last_seen = str(bot.get("last_seen", ""))
        print(f"FOUND|{status}|{last_seen}")
        raise SystemExit(0)
next_url = payload.get("next")
if next_url:
    print("NEXT")
else:
    print("NONE")
PY
)"

      if [[ "$parse_result" == FOUND\|* ]]; then
        found="1"
        IFS='|' read -r _ bot_status bot_last_seen <<< "$parse_result"
        if [ "$bot_status" = "online" ] && [ -n "$bot_last_seen" ] && [ "$bot_last_seen" != "None" ]; then
          echo "  ✓ Bot 已在线 (status=${bot_status}, last_seen=${bot_last_seen})"
          return 0
        fi
        # Best-effort fallback based on nonebot-dicepp standalone API contract:
        # when bot is registered but not yet online, trigger /dpp/heartbeat once.
        curl -fsS -X POST "http://127.0.0.1:${BOT_PORT}/dpp/heartbeat" > /dev/null 2>&1 || true
        break
      fi

      if [ "$parse_result" = "NEXT" ]; then
        page=$((page + 1))
      else
        break
      fi
    done

    retry=$((retry + 1))
    if [ "$found" = "1" ]; then
      printf "  已找到 Bot 记录，等待在线心跳... (%d/%d)\n" "$retry" "$max_retry"
    else
      printf "  等待注册记录出现... (%d/%d)\n" "$retry" "$max_retry"
    fi
    sleep 2
  done

  echo "❌ Bot 业务健康检查超时"
  return 1
}

dev_with_bot() {
  local bot_id=""
  local hub_url="http://backend:8000"
  local master_id="admin"
  local nickname="StandaloneBot"
  local bot_port="8080"
  local health_timeout="60"

  while [ $# -gt 0 ]; do
    case "$1" in
      --bot-id)
        bot_id="${2:-}"
        shift 2
        ;;
      --hub-url)
        hub_url="${2:-}"
        shift 2
        ;;
      --master-id)
        master_id="${2:-}"
        shift 2
        ;;
      --nickname)
        nickname="${2:-}"
        shift 2
        ;;
      --bot-port)
        bot_port="${2:-}"
        shift 2
        ;;
      --health-timeout)
        health_timeout="${2:-}"
        shift 2
        ;;
      *)
        echo "❌ 未知参数: $1"
        echo ""
        show_help
        exit 1
        ;;
    esac
  done

  if [ -z "$bot_id" ]; then
    echo "❌ dev-with-bot 缺少必填参数: --bot-id"
    echo ""
    show_help
    exit 1
  fi

  if ! [[ "$bot_id" =~ ^[0-9]+$ ]]; then
    echo "❌ --bot-id 必须为纯数字字符串"
    exit 1
  fi
  if [ "${#bot_id}" -gt 20 ]; then
    echo "❌ --bot-id 长度不能超过 20 位"
    exit 1
  fi

  export BOT_ID="$bot_id"
  export HUB_URL="$hub_url"
  export MASTER_ID="$master_id"
  export NICKNAME="$nickname"
  export BOT_PORT="$bot_port"

  echo ""
  echo "▶ 启动 Web + Bot 联调环境..."
  echo "  - BOT_ID: $BOT_ID"
  echo "  - HUB_URL: $HUB_URL"
  echo "  - MASTER_ID: $MASTER_ID"
  echo "  - NICKNAME: $NICKNAME"
  echo "  - BOT_PORT: $BOT_PORT"
  $DC -f docker-compose.dev.yml --profile bot up -d

  wait_backend_health "$health_timeout" || { print_bot_failure_diagnostics; exit 1; }
  wait_bot_container_healthy "$health_timeout" || { print_bot_failure_diagnostics; exit 1; }
  wait_bot_registered_online "$health_timeout" || { print_bot_failure_diagnostics; exit 1; }

  echo ""
  echo "🎉 联调环境启动完成"
  echo ""
  echo "  服务地址："
  echo "    前端: http://\$(wsl hostname -I | awk '{print \$1}'):5173  (WSL2 IP, localhost:5173 在该环境下经常因 wslrelay 损坏无法访问)"
  echo "    后端: http://localhost:8000"
  echo "    Bot API: http://localhost:${BOT_PORT}"
  echo "  机器人状态：在线 (BOT_ID=${BOT_ID})"
}

logs_bot() {
  local tail_lines="100"
  local follow_flag=""

  while [ $# -gt 0 ]; do
    case "$1" in
      --tail)
        tail_lines="${2:-100}"
        shift 2
        ;;
      --follow|-f)
        follow_flag="-f"
        shift
        ;;
      *)
        echo "❌ 未知参数: $1"
        echo ""
        show_help
        exit 1
        ;;
    esac
  done

  $DC -f docker-compose.dev.yml --profile bot logs --tail "$tail_lines" $follow_flag bot
}

seed_test_data() {
  local profile="${1:-baseline}"
  echo ""
  echo "▶ 初始化测试夹具数据 (profile=${profile})..."
  $DC exec -T backend python manage.py seed_test_data --profile "$profile" --strict
  echo "  ✓ 测试夹具已初始化"
}

reset_test_data() {
  local profile="${1:-baseline}"
  local strict_arg="${2:-strict}"
  echo ""
  echo "▶ 重置测试夹具数据 (profile=${profile}, mode=${strict_arg})..."
  if [ "$strict_arg" = "--no-strict" ]; then
    $DC exec -T backend python manage.py reset_test_data --profile "$profile" --no-strict
  else
    $DC exec -T backend python manage.py reset_test_data --profile "$profile"
  fi
  echo "  ✓ 测试夹具已重置"
}

verify_test_data() {
  local profile="${1:-baseline}"
  echo ""
  echo "▶ 校验测试夹具数据 (profile=${profile})..."
  $DC exec -T backend python manage.py verify_test_data --profile "$profile"
  echo "  ✓ 测试夹具校验通过"
}

show_help() {
  echo "用法：$0 <命令>"
  echo ""
  echo "命令:"
  echo "  rebuild           重建开发环境（停止、构建、迁移）"
  echo "  start             启动开发环境"
  echo "  stop              停止开发环境"
  echo "  status            查看环境状态"
  echo "  test              运行后端测试 + 前端 lint"
  echo "  lint              代码检查"
  echo "  check             运行测试 + 代码检查"
  echo "  restart-frontend  只重启前端服务（修改网页布局时使用）"
  echo "  restart-backend   只重启后端服务（修改后端代码时使用）"
  echo "  seed-test-data    初始化测试夹具数据"
  echo "  reset-test-data   重置测试夹具数据"
  echo "  verify-test-data  校验测试夹具完整性"
  echo "  dev-with-bot      启动 Web + Standalone Bot 联调环境（需 --bot-id）"
  echo "  logs-bot          查看 Bot 容器日志"
  echo "  help              显示帮助"
  echo ""
  echo "示例:"
  echo "  bash scripts/dev.sh rebuild"
  echo "  bash scripts/dev.sh test"
  echo "  bash scripts/dev.sh check"
  echo "  bash scripts/dev.sh restart-frontend"
  echo "  bash scripts/dev.sh restart-backend"
  echo "  bash scripts/dev.sh seed-test-data [profile]"
  echo "  bash scripts/dev.sh reset-test-data [profile] [--no-strict]"
  echo "  bash scripts/dev.sh verify-test-data [profile]"
  echo "  bash scripts/dev.sh dev-with-bot --bot-id 123456789 [--hub-url http://backend:8000] [--master-id admin] [--nickname StandaloneBot] [--bot-port 8080] [--health-timeout 60]"
  echo "  bash scripts/dev.sh logs-bot [--tail 100] [--follow]"
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
  restart-frontend)
    restart_frontend
    ;;
  restart-backend)
    restart_backend
    ;;
  seed-test-data)
    seed_test_data "${2:-baseline}"
    ;;
  reset-test-data)
    reset_test_data "${2:-baseline}" "${3:-strict}"
    ;;
  verify-test-data)
    verify_test_data "${2:-baseline}"
    ;;
  dev-with-bot)
    dev_with_bot "${@:2}"
    ;;
  logs-bot)
    logs_bot "${@:2}"
    ;;
  help|--help|-h|"")
    show_help
    ;;
  *)
    echo "未知命令：$COMMAND"
    echo ""
    show_help
    exit 1
    ;;
esac
