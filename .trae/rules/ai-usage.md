# AI 使用标准

## 通用准则

- 优先采用简单、最小化的实现方案，只在明确需要时才增加复杂度
- 保持变更范围紧密聚焦于请求的目标

## 环境架构

### 开发环境 (本地)

- **操作系统**: Windows + WSL2 (Ubuntu 22.04)
- **Docker**: 运行在 WSL2 中
- **访问方式**: 在 WSL 终端中执行 docker 命令

```
Windows <-> WSL2 (Ubuntu) <-> Docker
```

### 生产环境 (云服务器)

- **操作系统**: Ubuntu 22.04/24.04
- **Docker**: 原生安装
- **访问方式**: SSH 到服务器执行命令

### 常用命令 (在 WSL 中执行)

```bash
# 开发环境
bash scripts/dev.sh rebuild   # 重建开发环境
bash scripts/dev.sh test     # 运行测试
bash scripts/dev.sh check    # 完整检查

# 登录服务器 (生产环境)
ssh user@your-server-ip

# 生产环境命令 (在服务器上执行)
docker compose -f docker-compose.yml up -d --build
```

### Agent 运行命令 (WSL)

由于 Docker 运行在 WSL 中，Agent 需要通过 WSL 执行命令：

**步骤 1: 查询 WSL 发行版名称**

```powershell
wsl -l -v
```

输出示例：
```
  NAME                   STATE           VERSION
* Ubuntu                 Running         2
  docker-desktop         Running         2
  docker-desktop-data   Running         2
```

**步骤 2: 通过 WSL -d 执行命令**

```powershell
# 在指定发行版中执行命令
wsl -d Ubuntu -e bash -c "cd /mnt/c/Workspace/dungeon-toolkit-web && bash scripts/dev.sh check"

# 或者使用单行命令
wsl -d Ubuntu bash -c "docker compose -f docker-compose.dev.yml ps"
```

**注意事项：**
- 使用 `wsl -l -v` 查询实际的发行版名称（可能是 `Ubuntu`、`Ubuntu-22.04` 等）
- 项目路径在 WSL 中为 `/mnt/c/Workspace/dungeon-toolkit-web`
- 执行 docker 命令时确保 Docker daemon 在 WSL 中运行

## 数据来源

所有 D&D 规则内容数据的生成/更新，必须使用 `backend/data/parsers/` 目录下的解析脚本，**禁止凭记忆生成**。

### 解析脚本

```
backend/data/parsers/
├── common.py              # 公共工具函数
├── parse_races.py         # 种族数据
├── parse_spells.py        # 法术数据
├── parse_classes.py       # 职业数据
├── parse_backgrounds.py   # 背景数据
└── parse_items.py         # 物品数据
```

### 禁止行为

| 行为 | 说明 |
|------|------|
| AI 凭训练记忆编写规则数据 | 细节（范围、骰子、豁免）极易出错 |
| 直接修改 JSON 数据 | 必须使用 parsers 目录下的解析脚本 |
| 跳过 rules_source 直接写 JSON | 无法溯源 |

## 代码风格

- 实现应当最小化且聚焦
- 在编辑文件时保持变更范围紧凑
- 完成所有工作后再更新状态
