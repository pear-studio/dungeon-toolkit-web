---
alwaysApply: true
description: AI 通用准则
---
# AI 使用标准

## 通用准则
- 优先简单、最小化方案
- 变更聚焦于请求目标
- 遇不确定先询问

## 项目架构

```
dungeon-toolkit-web/
├── backend/           # Django 5.x + DRF (Python 3.12)
│   ├── apps/
│   │   ├── bots/      # 机器人管理
│   │   └── users/     # 用户认证 (JWT)
│   └── config/        # Django 配置
├── frontend/          # React 19 + TypeScript + Vite 7
│   └── src/
│       ├── pages/     # 页面组件
│       ├── components/# 复用组件
│       ├── stores/    # Zustand 状态
│       └── lib/       # 工具和常量
├── scripts/           # dev.sh 入口
└── docs/agent/        # AI Agent 规则
```

## 入口点
- 前端: `frontend/src/main.tsx` → `App.tsx`
- 后端: `backend/config/urls.py` → app routers
- 开发脚本: `bash scripts/dev.sh <command>`

## 开发环境
- Windows + WSL2 + Docker
- 项目路径: `/mnt/d/Workplace/dungeon-toolkit-web`

## 常用命令
```bash
bash scripts/dev.sh rebuild           # 重建环境
bash scripts/dev.sh start             # 启动容器
bash scripts/dev.sh stop              # 停止容器
bash scripts/dev.sh test              # 运行测试
bash scripts/dev.sh check             # 测试 + lint
bash scripts/dev.sh restart-frontend  # 重启前端
bash scripts/dev.sh restart-backend   # 重启后端
```

## Agent 执行命令
```powershell
# Windows 中通过 WSL 执行
wsl -d Ubuntu bash -c "cd /mnt/d/Workplace/dungeon-toolkit-web && bash scripts/dev.sh check"
```

## 代码风格
- 最小化变更范围
- 保持现有代码风格一致
- 完成后再更新状态

## 规范文件
- Agent 规则: `docs/agent/rules/`
- 后端详细规范: `backend/rules.md`
- 前端详细规范: `frontend/rules.md`