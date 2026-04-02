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
- [ ] 5. seed baseline 夹具并(可选)校验
- [ ] 6. 启动前端 Vite(WSL, 与 start-test-env 一致)
- [ ] 7. 基础健康检查与 /api 代理抽检(见 start-test-env)
- [ ] 8. 向用户输出 URL, fixture 账号提示, 真机器人注意点
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

### 5) 夹具数据("伪装数据")

默认写入 **baseline** profile(固定用户 + 夹具机器人等), 与手测文档一致:

```bash
docker compose -f docker-compose.dev.yml exec -T backend python manage.py seed_test_data --profile baseline --strict
```

或使用仓库脚本(WSL 内, `cd` 到项目根):

```bash
bash scripts/dev.sh seed-test-data baseline
```

可选完整性校验:

```bash
bash scripts/dev.sh verify-test-data baseline
```

其他 profile(如空广场)见 `docs/testing.md`, **不要**在用户未要求时擅自切换 profile.

### 6) 启动前端开发服务

与 `start-test-env` 一致, **推荐在 WSL 中**启动, 减少 Windows/WSL 与 Vite 代理到 `localhost:8000` 的坑:

```bash
cd "$REPO_WSL/frontend" && npm run dev -- --host 0.0.0.0 --port 5173
```

> 若用户坚持用 Docker 里的 `frontend` 服务代替 Vite 本机进程, 可 `docker compose ... up -d frontend`, 行为以 `docker-compose.dev.yml` 为准(`VITE_API_BASE_URL` 指向容器内 `backend`). 与 `start-test-env` 的推荐路径不完全相同, 需在汇报中说明采用的是哪一套.

### 7) 验证

- 基础连通性抽检（health + `/api/...`）：按 `start-test-env` 第 2 和 4 步执行并确认。
- ws acceptance 的更深入诊断/鉴权/证据自检见 `../test-guide/SKILL.md`。

### 8) 向用户交付的信息

- 前端: `http://localhost:5173/`
- 后端: `http://localhost:8000/`
- 登录手测: 优先 `docs/testing.md` 中的 **fixture_*** 账号与密码(如 `fixture_normal` / `FixturePass1234`).
- **真实机器人**: 终端进程需能访问注册 URL(见下节); 网页端登录后在产品流程里**绑定**已有 `bot_id`.

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
