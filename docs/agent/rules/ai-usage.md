# AI 使用标准

## 通用准则

- 优先简单、最小化方案
- 变更聚焦于请求目标
- 遇不确定先询问

## 开发环境

- Windows + WSL2 + Docker
- 项目路径: `/mnt/d/Workplace/dungeon-toolkit-web`

## 常用命令

```bash
# 在 WSL 中执行
bash scripts/dev.sh rebuild   # 重建环境
bash scripts/dev.sh test      # 运行测试
bash scripts/dev.sh check     # 完整检查
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

Agent 规则（简要）：
- `docs/agent/rules/backend.md` - 后端快速参考
- `docs/agent/rules/frontend.md` - 前端快速参考

详细开发规范：
- `backend/rules.md` - 后端完整示例
- `frontend/rules.md` - 前端完整示例
