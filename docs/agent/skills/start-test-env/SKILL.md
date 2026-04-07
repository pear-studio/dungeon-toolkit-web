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

This machine has a three-layer network stack:

```
Windows (Browser / PowerShell / Git Bash)
    |
    v
WSL2 VM (Ubuntu)
    |
    v
Docker containers (frontend/backend)
```

**Note**: This WSL distro does **not** have native Node.js. Running `npm run dev` inside WSL actually launches the **Windows `node.exe`** process via `/init` relay, causing port conflicts.

**Therefore**:
- Do **not** run `npm run dev` inside WSL.
- Always start the frontend with `docker compose up -d frontend`.

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
- [ ] 6. Report URLs, API endpoints, and test accounts
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

**Use Docker frontend container** (mandatory — never run `npm run dev` inside WSL in this environment, because it spawns Windows `node.exe` and causes port conflicts):

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml up -d frontend"
```

Expected: container status `Up`.

### 4) Verify proxy connectivity

From Windows shell, test the API proxy:

```powershell
curl.exe -i --max-time 10 http://localhost:5173/api/bots/
```

Expected: HTTP `200` and JSON body.

### 6) Report ready state

Provide:
- Frontend URL: `http://localhost:5173/`
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

## Network Stability Tips

WSL2 may automatically suspend after extended periods of inactivity, causing network interruptions. If you encounter connection issues:

1. Run any WSL command to wake it up (e.g., `wsl ls`)
2. Or keep a WSL terminal window open during development

### Keep-Alive (optional)

Use this heartbeat command every 2-3 minutes:
```powershell
wsl bash -c "echo keepalive"
```

## Troubleshooting

### Case A: `localhost:5173` unreachable

1. Confirm container is up: `wsl bash -c "docker ps"`.
2. Verify from inside WSL: `wsl bash -c "curl -s http://localhost:5173/"`.
3. Check for port conflicts on Windows: `netstat -ano | findstr :5173`
4. Restart the frontend container: `docker compose -f docker-compose.dev.yml restart frontend`

### Case B: Port 5173 already in use

Find and stop the process:

```powershell
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

Then restart the frontend container:

```powershell
wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml restart frontend"
```

### Case C: Connection drops after inactivity

WSL2 may have suspended. Wake it up:
```powershell
wsl ls
```

Or restart the environment:
```powershell
wsl --shutdown
# Then restart the stack
```

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
