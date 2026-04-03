---
name: start-local-test-env
description: 启动本地 test 栈: 先按 run-tests 做 pytest + lint, 再于 WSL 拉起 db/backend, 写入 baseline 夹具, 并启动前端开发服务; 说明夹具数据与真实机器人注册的关系及未决边界.
---

# 启动本地 test 环境(预检 + 夹具 + 前后端)

## 目的

在用户要**手测网页功能**时, 用固定顺序把环境拉齐:

1. **基线正确**: 按 [`run-tests`](../run-tests/SKILL.md) 的思路跑通 pytest 与前端 lint(避免在坏基线上浪费时间).
2. **可访问端口**: backend `8000`, 浏览器走 Vite(推荐 `5173` + `/api` 代理).
3. **夹具数据**: 开发库里写入 **baseline** 测试夹具(固定账号 / 示例机器人等), 便于登录与列表演示; **不是**"假后端纯内存"模式, 仍是真实 Django + PostgreSQL.
4. **真实机器人**: 本仓库没有单独的"模拟器开关". **夹具机器人**在 DB 里; **真实 QQ 机器人进程**需能访问本机(或局域网)上的注册接口, 自行完成登记后再在网页端绑定.

## 环境结构警告: Windows → WSL → Docker 三层网络

这台机器上的网络栈是**三层结构**, Agent 非常容易在这里踩坑:

```
Windows (浏览器 / PowerShell / Git Bash)
    |
    |-- wslrelay.exe (负责 localhost 端口转发, 非常脆弱)
    v
WSL2 VM (Ubuntu, 例: 172.21.200.199)
    |
    |-- docker-proxy
    v
Docker 容器 (frontend/backend 在 172.18.0.x 网段)
```

**致命陷阱**: 这台 WSL 里**没有原生 Node.js**。如果在 WSL 中执行 `npm run dev`, 实际上会透过 `/init` 代理启动** Windows 侧的 `node.exe`**。这个 `node.exe` 会直接抢占 Windows 的 `localhost:5173`, 与 `wslrelay.exe` 的转发规则冲突。即便之后杀掉了 `node.exe`, `wslrelay.exe` 对 `5173` 的映射也**经常永久失效**（`localhost:8000` 通常不受影响）。

**因此**:
- **严禁**在 WSL 中执行 `npm run dev` 来启动前端。
- 前端**必须**用 `docker compose up -d frontend` 启动。
- 向用户汇报 URL 时, **优先使用 WSL2 IP** (如 `http://172.21.200.199:5173/`), 只有在明确验证过 Windows 侧 `localhost:5173` 可用时, 才能推荐使用 localhost。

## 与现有技能的关系

| 技能 | 作用 |
|------|------|
| `run-tests` | Docker 检查, pytest, `npm run lint` 的规范与 Windows/WSL 注意点 |
| `start-test-env` | 只拉起环境与健康检查, **不包含**预检与 `seed_test_data` |
| `test-guide` | ws acceptance 前置自检: health/诊断端点/鉴权/证据留档 |
| **本技能** | 编排: **预检 → 夹具 → 起服务 → 汇报 URL**, 并写明真机对接的灰区 |

实现时: **不要与本条重复长篇命令**, 细节以 `run-tests`, `start-test-env` 为准; 此处给**必选顺序**与**路径占位符**.

## 前置(请先确认)

以下若与用户机器不一致, 需在执行前替换命令中的路径与发行版名.

- **WSL 发行版**: 下文默认 `Ubuntu`(与 `docs/agent/rules/ai-usage.md` 一致).
- **仓库在 WSL 中的路径**: 下文默认 `/mnt/d/Workplace/dungeon-toolkit-web`, 若仓库不在 `D:`, 改成实际挂载路径.
- **PowerShell 无 `docker`**: 所有 `docker compose` 须在 WSL 内执行, 或 `wsl -d Ubuntu bash -lc '...'` 包一层.

定义占位符(全文替换一次即可):

```text
WSL_DISTRO=Ubuntu
REPO_WSL=/mnt/d/Workplace/dungeon-toolkit-web
```

## 标准流程(按顺序执行)

将下列清单复制到对话并逐项打勾:

```text
- [ ] 1. WSL 中确认 Docker 可用(同 run-tests 第 1 步)
- [ ] 2. 拉起 db + backend(不必先起 frontend 容器)
- [ ] 3. 后端 pytest 通过
- [ ] 4. 前端 lint 通过(frontend 容器未起时用备选命令)
- [ ] 5. seed baseline 夹具并创建管理员账号
- [ ] 6. 启动前端容器(严禁在 WSL 里跑 `npm run dev`)
- [ ] 7. 基础健康检查与 /api 代理抽检(见 start-test-env)
- [ ] 8. 向用户输出 WSL2 IP 形式的 URL, fixture 和管理员账号, 真机器人注意点, **并提醒保持 WSL 终端打开**
```

### 1) Docker

按 `run-tests`: **在 WSL 中**执行 `docker info`, 失败则停止并提示启动 Docker.

### 2) 起后端栈

```bash
docker compose -f docker-compose.dev.yml up -d db backend
```

(PowerShell 调用示例: `wsl -d Ubuntu bash -lc "cd /mnt/d/Workplace/dungeon-toolkit-web && docker compose -f docker-compose.dev.yml up -d db backend"`)

### 3) Pytest

```bash
docker compose -f docker-compose.dev.yml exec -T backend pytest -v --tb=short
```

### 4) 前端 Lint

**优先**(与 `run-tests` 一致): 若已 `up -d frontend`, 则

```bash
docker compose -f docker-compose.dev.yml exec -T frontend npm run lint
```

**备选 A**(常见: 只起了 db/backend, 不想起长期 frontend 容器):

```bash
docker compose -f docker-compose.dev.yml run --rm -T frontend npm run lint
```

**备选 B**: 在 WSL 主机目录(已 `npm install`):

```bash
cd "$REPO_WSL/frontend" && npm run lint
```

### 5) 夹具数据与管理员账号

**先写入 baseline 夹具** (固定用户 + 夹具机器人):

```bash
docker compose -f docker-compose.dev.yml exec -T backend python manage.py seed_test_data --profile baseline --strict
```

或使用仓库脚本:

```bash
bash scripts/dev.sh seed-test-data baseline
```

**再创建管理员和测试账号** (用于 Django Admin):

```bash
docker compose -f docker-compose.dev.yml exec -T backend python manage.py create_test_users
```

这会创建:
- `admin / AdminPass1234` (超级管理员, 可登录 Django Admin)
- `testuser / TestPass1234` (普通测试用户)
- `runner / RunnerPass1234` (CI/CD 测试用户)

可选完整性校验:

```bash
bash scripts/dev.sh verify-test-data baseline
```

其他 profile 见 `docs/testing.md`, **不要**在用户未要求时擅自切换 profile.

### 6) 启动前端开发服务

**必须通过 Docker 容器启动前端**, 严禁在 WSL 中执行 `npm run dev` (原因见上文的"环境结构警告"):

```bash
docker compose -f docker-compose.dev.yml up -d frontend
```

这样前端会在 Docker 网络中与 backend 共处同一上下文, `VITE_API_BASE_URL` 等配置以 `docker-compose.dev.yml` 为准。

### 7) 验证

- 基础连通性抽检（health + `/api/...`）：按 `start-test-env` 第 2 和 4 步执行并确认。
- ws acceptance 的更深入诊断/鉴权/证据自检见 `../test-guide/SKILL.md`。

### 8) 向用户交付的信息

- 前端: `http://172.21.200.199:5173/` (WSL2 IP; 如 IP 变动, 以 `wsl hostname -I` 第一列为准).
  - `localhost:5173` 在此环境下经常因 `wslrelay.exe` 损坏而无法访问, 不要默认推荐.
- 后端基础地址: `http://localhost:8000/`
- **可用 API 端点** (以列表形式清晰呈现, **不要提示** `/api/docs/` 因为该路径不存在):
  - 健康检查: `http://localhost:8000/api/health/`
  - 机器人列表: `http://localhost:8000/api/bots/`
  - 认证接口: `http://localhost:8000/api/auth/`
  - 管理后台: `http://localhost:8000/admin/`
- **前端登录账号** (fixture 用户):
  - `fixture_normal / FixturePass1234` (正常场景)
  - `fixture_expired / FixturePass1234` (token 过期场景)
  - `fixture_refresh_fail / FixturePass1234` (refresh 失败场景)
- **后端管理账号** (Django Admin):
  - `admin / AdminPass1234` (超级管理员)
  - `testuser / TestPass1234` (普通测试用户)
- **真实机器人**: 终端进程需能访问注册 URL(见下节); 网页端登录后在产品流程里**绑定**已有 `bot_id`.
- **⚠️ 必须提醒用户**: 打开一个独立终端并执行 `wsl` 保持 WSL 会话活跃。如果几分钟后连接中断，执行任意 WSL 命令（如 `wsl ls`）即可唤醒。

---

## 重要: 保持 WSL 终端打开 (防止 WSL2 休眠断网)

**关键**: WSL2 在几分钟无活动后会自动休眠, 导致 Windows 与 Docker 容器之间的网络桥接 (`wslrelay.exe`) 中断。**开发期间必须保持 WSL 终端窗口打开**。

### 解决方案

启动环境后, **打开一个独立的终端窗口**并保持 WSL 会话:

```powershell
wsl
```

只要终端保持开启（不需要执行任何命令）, WSL2 就不会休眠, 网络连接保持稳定。

如果忘记打开终端导致连接中断:
1. 执行任意 WSL 命令（如 `wsl ls`）即可唤醒
2. 或切换到已打开的 WSL 终端窗口

### 替代方案（如果没有终端窗口）

每 2-3 分钟执行一次心跳命令:
```powershell
wsl bash -c "echo keepalive"
```

---

## 真实机器人 vs 夹具数据(语义说明)

| 类型 | 含义 |
|------|------|
| 夹具机器人 | `seed_test_data` 写入 DB 的示例 `Bot` 记录, 固定 `api_key` 规则见后端夹具代码; 用于列表 / 绑定等 UI 演示. |
| 真实机器人 | 独立进程(QQ 侧客户端)调用 **公开** 注册接口在 DB 中创建或更新记录, 并获得 `api_key`; 与开发库是否已 seed **无强制互斥**, 但同一 `bot_id` 再次注册会走更新逻辑, 注意勿与夹具 ID 冲突. |

注册接口路径(部署在本地 backend 时):

```text
POST http://<对机器人进程可达的主机>:8000/api/bots/register/
```

心跳等见 `backend/apps/bots/urls.py` 下其余路由.

---

## 模糊或未在仓库中钉死的点(实施前建议与用户确认)

以下内容在本技能中**只作提示**, 避免 Agent 假装已有唯一答案:

1. **机器人进程看到的 "后端地址"**  
   本地手测时, 客户端在**同一台 Windows** 上可能需填 `http://127.0.0.1:8000`; 若在**另一设备**, 需填开发机局域网 IP, 并注意防火墙; 在 **WSL 独有网络**场景下, 还可能与 Windows `localhost` 不一致.

2. **HTTPS / 域名**  
   若真实客户端强制 HTTPS 或回调域名, 本地 HTTP 可能无法完整模拟; 是否用内网穿透或临时证书属于环境决策, 仓库未规定.

3. **数据隔离**  
   `seed_test_data baseline` 会写/更新开发库; 真实注册也会写同一库. 是否需要: 测试前 `reset-test-data`, 单独 profile, 或独立 Docker volume, 应由团队约定.

4. **"支持连接真实机器人"的验收标准**  
   本技能将其定义为: 后端开发环境可达 + 注册/心跳 API 按文档可被调用; **不**保证未文档化的 QQ 侧插件配置逐步指引.

5. **lint 与 frontend 镜像**  
   备选 `docker compose run frontend npm run lint` 依赖镜像已构建; 若首次构建失败, 改用 WSL 内 `frontend/npm run lint`.

---

## Agent 退出准则

- pytest 或 lint 任一失败: **停止**, 只汇报失败摘要并引用 `run-tests` 修复路径, 不继续 seed 与手测 URL.
- 健康检查或代理抽检失败: 优先对照 `start-test-env` 排错小节.
- 所有自动化步骤通过后, 再输出 fixture 账号与真实机器人网络注意点.
