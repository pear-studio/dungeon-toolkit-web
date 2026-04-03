---
name: start-test-env
description: Start frontend and backend test environment for dungeon-toolkit-web, verify health and API proxy, and troubleshoot Windows/WSL connectivity. Use when user asks to run local test servers, start dev environment, or fix localhost proxy failures.
---

# Start Test Environment

## Purpose

Boot the project test environment quickly and consistently:
- Start backend (`db` + `backend`) with Docker Compose in WSL.
- Start frontend Vite dev server **inside Docker** (not via `npm run dev` in WSL).
- Verify frontend-to-backend proxy connectivity.
- Provide stop/cleanup commands.

## Important: Windows + WSL + Docker Network Architecture

This machine has a **three-layer network stack** that agents frequently misunderstand:

```
Windows (Browser / PowerShell / Git Bash)
    |
    |-- wslrelay.exe (localhost port forwarding, fragile)
    v
WSL2 VM (Ubuntu, e.g. 172.21.200.199)
    |
    |-- docker-proxy
    v
Docker containers (frontend/backend on 172.18.0.x)
```

**The trap**: Because this WSL distro does **not** have native Node.js, running `npm run dev` inside WSL actually launches the **Windows `node.exe`** process via `/init` relay. That Windows `node.exe` seizes `localhost:5173` on the Windows side, colliding with `wslrelay.exe`'s port forwarding rule. Even after the process is killed, `wslrelay.exe` often **never recovers** the `localhost:5173` mapping (while `localhost:8000` usually remains fine).

**Therefore**:
- Do **not** run `npm run dev` inside WSL.
- Always start the frontend with `docker compose up -d frontend`.
- When reporting access URLs, prefer the **WSL2 IP** (e.g. `http://172.21.200.199:5173/`) over `http://localhost:5173/` unless you have explicitly verified localhost works from Windows.

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
- [ ] 2. Create admin and test users
- [ ] 3. Verify backend health endpoint
- [ ] 4. Start frontend container (NEVER run `npm run dev` in WSL)
- [ ] 5. Verify /api proxy from frontend endpoint
- [ ] 6. Report URLs, API endpoints, test accounts, and WSL keepalive reminder
```

### 1) Start backend in WSL

Run from repo root:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml up -d db backend"
```

### 2) Create admin and test users

Create the Django admin account and test users for backend access:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml exec -T backend python manage.py create_test_users"
```

This creates:
- `admin / AdminPass1234` (superuser for Django Admin)
- `testuser / TestPass1234` (regular test user)
- `runner / RunnerPass1234` (CI/CD test user)

### 3) Verify backend health

```powershell
wsl -d Ubuntu bash -lc "curl -fsS http://localhost:8000/api/health/"
```

Expected: JSON containing `"status":"ok"`.

WebSocket 测试使用 pytest：`pytest apps/bots/tests/test_websocket_gateway.py -v`

### 3) Start frontend

**Use Docker frontend container** (mandatory — never run `npm run dev` inside WSL in this environment, because it spawns Windows `node.exe` and breaks `localhost:5173` port forwarding permanently):

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml up -d frontend"
```

Expected: container status `Up`.

### 4) Verify proxy connectivity

From Windows shell, test via the **WSL2 IP** (replace `172.21.200.199` with the actual IP from `wsl hostname -I`):

```powershell
curl.exe -i --max-time 10 http://172.21.200.199:5173/api/bots/
```

Expected: HTTP `200` and JSON body.

> `localhost:5173` may fail from Windows even when the container is healthy, because `wslrelay.exe` forwarding for 5173 is fragile in this environment. Always verify with the WSL2 IP first.

### 6) Report ready state

Provide:
- Frontend URL: `http://172.21.200.199:5173/` (WSL2 IP; mention that `localhost:5173` can be used only if explicitly verified)
- Backend base URL: `http://localhost:8000/`
- **Available API endpoints** (present as a clear list, do **not** mention `/api/docs/` as it does not exist):
  - Health: `http://localhost:8000/api/health/`
  - Bots: `http://localhost:8000/api/bots/`
  - Auth: `http://localhost:8000/api/auth/`
  - Admin: `http://localhost:8000/admin/`
- **Test accounts** (present clearly):
  - Django Admin: `admin / AdminPass1234`
  - Test user: `testuser / TestPass1234`
  - CI user: `runner / RunnerPass1234`
- Proxy check result for `/api/bots/`
- **⚠️ Important reminder to user**: Open a separate terminal and run `wsl` to keep the WSL session alive. If the connection drops after a few minutes, execute any WSL command (e.g., `wsl ls`) to wake it up.

## Important: Keep WSL Terminal Open (WSL2 Idle Timeout)

**Critical**: WSL2 VM will automatically suspend after a few minutes of inactivity, which breaks the network bridge (`wslrelay.exe`) between Windows and Docker containers. **To prevent this, keep a WSL terminal window open during development.**

### Solution

After starting the environment, open a separate terminal and run:

```powershell
wsl
```

This keeps the WSL session alive, ensuring the network bridge remains active. You don't need to run any commands inside — just having the terminal open is sufficient.

If you forget and the connection drops after a few minutes:
1. Execute any WSL command (e.g., `wsl ls`) to wake it up
2. Or switch to the already-open WSL terminal

### Alternative (if no terminal available)

Use this heartbeat command every 2-3 minutes:
```powershell
wsl bash -c "echo keepalive"
```

## Troubleshooting

### Case A: `localhost:5173` unreachable but WSL2 IP works

This is expected in this environment due to the `wslrelay.exe` / `node.exe` conflict described above. Do **not** waste time trying to fix `localhost:5173` unless the user explicitly requires it. Simply switch the reported URL to the WSL2 IP.

### Case B: Port 5173 already in use on Windows

Find and stop the Windows `node.exe` or other process:

```powershell
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

Then restart the frontend container (not `npm run dev`):

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml restart frontend"
```

### Case C: Neither localhost nor WSL2 IP works from Windows

1. Confirm container is up inside WSL: `wsl bash -c "docker ps"`.
2. Confirm WSL internal access works: `wsl bash -c "curl -s http://172.21.200.199:5173/"`.
3. If step 2 works but Windows cannot reach the IP, `wslrelay.exe` or the WSL vEthernet bridge is in a bad state. Run `wsl --shutdown` and restart the stack.

## Stop Commands

Stop frontend: terminate its terminal process.

Stop backend stack:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml down"
```

## Notes

- Keep changes minimal: this skill is for runtime environment operations, not feature implementation.
- Always report whether failures are from backend unavailability or frontend proxy path/network issues.
- WebSocket 测试已迁移到 pytest，运行 `pytest apps/bots/tests/test_websocket_gateway.py -v`
