---
name: test-guide
description: Start by checking environment & prerequisites before running ws acceptance/tests.
---

# 测试前自检（简洁版）

## 你要先确认什么
- 运行环境是否“干净可复现”：上一次验收是否已退出；是否还残留了 `ws_acceptance.py` / 卡住的 Python 进程。
- 后端是否可用：`GET /api/health/` 返回 `{"status":"ok"}`。
- 诊断端点是否存在：`DEBUG=True` 时 `/api/debug/ws-status/<bot_pk>/` 才会注册（否则应直接 404）。
- 诊断权限是否满足：诊断接口需要 `IsAdminUser`（必须使用 admin token）。
- 依赖是否齐全：`ws_acceptance.py` 需要 `aiohttp`（若容器没装过，先补依赖）。
- 访问路径是否可靠：尽量在 **backend 容器内**运行验收脚本，避免 Windows↔WSL 端口连通性问题。

## 基础连通性检查（快速版）
- 后端健康：WSL 内执行 `curl -fsS http://localhost:8000/api/health/`，期望含 `"status":"ok"`。
- 前端代理：若前端 Vite 在 `5173`，从 Windows 执行 `curl.exe -i --max-time 10 http://localhost:5173/api/bots/`，期望 `200` 与 JSON。
- 若这里失败：优先参照 `start-test-env` 的排错小节（通常是 Windows/WSL 网络不一致或端口占用）。
- 如需更深入的 ws 诊断/鉴权/证据留档，请继续往下按本 skill 的 preflight 走（不是只做连通性）。

## 如果你要用 `--seed`
- 一定使用唯一的 `--run-id`（避免账号/机器人冲突）。
- 用固定前缀 `--acceptance-prefix` 来隔离数据，避免污染真实数据。
- 推荐总是配对使用 `--seed --cleanup`（结束后自动清理）。

## 建议的最小执行顺序
```text
1) 先跑脚本的 preflight（脚本启动后会自动做）
2) preflight 通过再进入 Gate/场景
3) 生成的 jsonl 证据留档，失败时只先修环境/鉴权问题
```

## 失败时优先检查
- `api_health` / `diagnostic_accessible` 失败：先处理后端可达性、DEBUG、admin token。
- `db_online` / `consistent` 波动：通常是网关刚连上到落库的短延迟，优先看是否需要重跑或检查 Gate 等待逻辑。
- `ws` 断连/踢出异常：确认 bot/token 是否对应同一 bot_pk 与同一 user。

