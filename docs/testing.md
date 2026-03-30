# 测试指南

## 概述

本文档介绍当前仓库的测试方式与测试目录. 当前后端业务 app 主要为 `users` 与 `bots`.

## 测试框架

- **pytest** - Python 主流测试框架
- **pytest-django** - Django 集成
- **pytest-cov** - 覆盖率报告
- **factory-boy** - 测试数据工厂

## 快速开始

### 本地运行(不使用 Docker)

```bash
cd backend
pip install -r requirements.txt

# 运行所有测试
pytest

# 运行指定模块测试
pytest apps/users/tests/
pytest apps/bots/tests.py

# 运行带覆盖率报告
pytest --cov=. --cov-report=html
```

### Docker 运行

```bash
# 启动开发环境
docker compose -f docker-compose.dev.yml up -d --build

# 在后端容器中运行测试
docker compose -f docker-compose.dev.yml exec backend pytest
```

### 使用项目脚本运行

```bash
# 后端 pytest + 前端 lint
bash scripts/dev.sh test

# 前端 lint
bash scripts/dev.sh lint

# test + lint
bash scripts/dev.sh check
```

## 初始化测试夹具

```bash
cd backend
python manage.py seed_test_data --profile baseline --strict

# 或使用统一脚本(推荐)
bash scripts/dev.sh seed-test-data baseline
bash scripts/dev.sh verify-test-data baseline
bash scripts/dev.sh reset-test-data baseline
# 宽松模式(调试坏环境时使用)
bash scripts/dev.sh reset-test-data baseline --no-strict
```

## 固定测试账号矩阵

| 用户名 | 密码 | 场景 | 用途 |
|--------|------|------|------|
| fixture_normal | FixturePass1234 | 正常登录 | 常规点击/登录/个人页验证 |
| fixture_expired | FixturePass1234 | access 过期恢复 | 验证 refresh 成功后恢复会话 |
| fixture_refresh_fail | FixturePass1234 | refresh 失败 | 验证清理登录态并跳转 `/login` |

> 兼容账号 `testuser/admin/runner` 仍可通过 `create_test_users` 创建, 但回归清单优先使用 `fixture_*` 账号.

## 测试结构

```
backend/
├── pytest.ini               # pytest 配置
├── tests/
│   └── factories.py         # 测试数据工厂
└── apps/
    ├── users/
    │   └── tests/
    │       ├── test_models.py
    │       ├── test_serializers.py
    │       └── test_views.py
    └── bots/
        └── tests.py
```

## 测试数据工厂

项目使用 `factory-boy` 创建测试数据:

```python
from tests.factories import UserFactory

user = UserFactory()
```

## 常见问题

### 数据库连接错误

确保环境变量正确配置(示例):

```env
DB_NAME=dungeon_toolkit
DB_USER=dungeon_toolkit
DB_PASSWORD=dungeon_toolkit
```

### ImportError

确保在 `backend/` 目录运行测试, 且 Django settings 使用开发或测试配置.

## 前端回归检查(frontend-optimization-plan)

建议在本地或 dev 容器前端服务下执行以下手工回归:

- 机器人广场搜索:
  - 快速输入关键词时, 请求不应按每个按键都触发.
  - 搜索与状态筛选组合时, 加载/空态/错误态表现一致.
  - 快速连续切换关键词时, 页面应展示最后一次输入对应结果.
- 鉴权链路:
  - access token 失效时, 前端先走 refresh, 再重试原请求.
  - refresh 失败时, 前端清理 token 并跳转 `/login`, 且无循环重试.
- 路由行为:
  - 访问 `/robots/my`, `/robots/my/bind` 应重定向到 `/profile`.
  - 首次进入未预加载页面时显示统一加载占位.

## 手工回归脚本(从 reset 开始)

每次执行前建议从统一基线开始:

```bash
bash scripts/dev.sh reset-test-data
bash scripts/dev.sh verify-test-data
```

### 1) 正常登录与基础点击

- 使用 `fixture_normal / FixturePass1234` 登录.
- 验证个人页, 机器人广场加载正常.
- 搜索关键词 `alpha`, `beta`, 确认结果稳定且可重复.

### 2) `restoreSession -> /auth/me/ -> refresh` 成功分支

- 使用 `fixture_expired` 登录后, 在浏览器开发者工具中将 `access` token 替换为明显无效值(保留 `refresh`).
- 刷新页面触发会话恢复.
- 预期: 前端自动 refresh 一次并恢复登录态, 不进入循环请求.

### 3) refresh 失败分支

- 使用 `fixture_refresh_fail` 登录后, 同时将 `access` 与 `refresh` 置为无效值.
- 刷新页面触发会话恢复.
- 预期: 前端清理本地鉴权信息并跳转 `/login`.

### 4) 机器人广场空数据与错误态 Hook

- 空数据: 执行 `bash scripts/dev.sh reset-test-data empty-robot-plaza` 后访问机器人广场, 预期展示空态.
- 错误态: 保持页面打开并临时停止后端服务, 再触发广场请求, 预期展示错误态且可恢复.

## 夹具维护说明

- 新增夹具账号时, 优先使用 `fixture_` 前缀, 避免影响真实开发账号.
- 新增机器人夹具时, 使用固定 `bot_id` 并确保可重复 `update_or_create`.
- 若回归需要新增场景, 优先通过 `seed_test_data --profile <name>` 扩展 profile, 而不是手工改库.
- 修改夹具后请执行 `verify_test_data`, 并更新本页的账号矩阵与脚本步骤.
