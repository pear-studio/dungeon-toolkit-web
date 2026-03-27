---
name: project-onboard
description: >-
  Summarizes the Dungeon Toolkit repo, points to canonical docs, and lists test
  commands. Use when the agent lacks project context or needs a fast overview
  before exploring or implementing changes.
---

# Dungeon Toolkit — 快速 onboard

## 项目是做什么的

面向中文 D&D 5e 玩家的开源工具箱。单体仓库：**React 19 + TS + Vite**（`frontend/`）、**Django 4 + DRF**（`backend/`）、**PostgreSQL**，本地常用 **Docker Compose**（`docker-compose.dev.yml`）。

## 文档从哪读

| 用途 | 路径 |
|------|------|
| 项目简介与本地跑起来 | 仓库根目录 `README.md` |
| 开发 / 测试 / 部署 / 命令 | `docs/development.md`、`docs/testing.md`、`docs/deployment.md`、`docs/commands.md` |
| 后端约定 | `backend/rules.md`、`docs/agent/rules/backend.md` |
| 前端与 AI 使用约定 | `docs/agent/rules/frontend.md`、`docs/agent/rules/ai-usage.md` |
| Agent 链接脚本 | `docs/agent/link-to-cursor.bat` 等 |

深入实现时再打开对应 `backend/apps/`、`frontend/src/` 源码。

## 测试怎么跑（选一种环境）

**本地后端（需 venv，DB 按 README）**

```bash
cd backend
pytest
```

**容器（与 `.cursor/skills/run-tests` 一致：先起 dev compose）**

```bash
docker compose -f docker-compose.dev.yml up -d
docker compose exec -T backend pytest -v --tb=short
docker compose exec -T frontend npm run lint
```

**一键（bash/WSL）**

```bash
bash scripts/dev.sh test
```

更细的说明见 `docs/testing.md`。需要完整校验流程时跟随 **`run-tests`** 技能。
