---
name: start-test-env
description: Start frontend and backend test environment for dungeon-toolkit-web, verify health and API proxy, and troubleshoot Windows/WSL connectivity. Use when user asks to run local test servers, start dev environment, or fix localhost proxy failures.
---

# Start Test Environment

## Purpose

Boot the project test environment quickly and consistently:
- Start backend (`db` + `backend`) with Docker Compose in WSL.
- Start frontend Vite dev server.
- Verify frontend-to-backend proxy connectivity.
- Provide stop/cleanup commands.

## When to Use

Use this skill when the user asks to:
- "启动测试环境"
- "起前后端服务"
- "前端连不上后端"
- "localhost 出现 API 加载失败 / ECONNREFUSED"

## Standard Workflow

Copy this checklist and execute in order:

```text
- [ ] 1. Start backend containers in WSL
- [ ] 2. Verify backend health endpoint
- [ ] 3. Start frontend dev server
- [ ] 4. Verify /api proxy from frontend endpoint
- [ ] 5. Report URLs and current status
```

### 1) Start backend in WSL

Run from repo root:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml up -d db backend"
```

### 2) Verify backend health

```powershell
wsl -d Ubuntu bash -lc "curl -fsS http://localhost:8000/api/health/"
```

Expected: JSON containing `"status":"ok"`.

更深入的 ws acceptance 前置自检（诊断端点/权限/证据 jsonl）见 `../test-guide/SKILL.md`。

### 3) Start frontend

Preferred (same network context as backend):

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web/frontend && npm run dev -- --host 0.0.0.0 --port 5173"
```

Expected: Vite shows `Local: http://localhost:5173/`.

### 4) Verify proxy connectivity

From Windows shell:

```powershell
curl.exe -i --max-time 10 http://localhost:5173/api/bots/
```

Expected: HTTP `200` and JSON body.

### 5) Report ready state

Provide:
- Frontend URL: `http://localhost:5173/`
- Backend URL: `http://localhost:8000/`
- Health URL: `http://localhost:8000/api/health/`
- Proxy check result for `/api/bots/`

## Troubleshooting

### Case A: Vite proxy shows `ECONNREFUSED` to `localhost:8000`

Likely Windows and WSL network mismatch. Fix order:
1. Ensure backend is up in WSL (`docker compose ... ps`).
2. Prefer running frontend in WSL (Step 3 command above).
3. Re-test `http://localhost:5173/api/bots/`.

### Case B: Port 5173 already in use

Find and stop old process:

```powershell
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

Then restart frontend command.

### Case C: Backend healthy in WSL but not reachable from Windows localhost

Use WSL frontend process and test through Vite proxy (`/api/...`) instead of direct host-to-container assumptions.

## Stop Commands

Stop frontend: terminate its terminal process.

Stop backend stack:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml down"
```

## Notes

- Keep changes minimal: this skill is for runtime environment operations, not feature implementation.
- Always report whether failures are from backend unavailability or frontend proxy path/network issues.
- 如果要继续跑 ws acceptance（`ws_acceptance.py`），建议先按 `../test-guide/SKILL.md` 完成 preflight。
