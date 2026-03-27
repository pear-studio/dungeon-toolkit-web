# 测试指南

## 概述

本文档介绍当前仓库的测试方式与测试目录。当前后端业务 app 主要为 `users` 与 `bots`。

## 测试框架

- **pytest** - Python 主流测试框架
- **pytest-django** - Django 集成
- **pytest-cov** - 覆盖率报告
- **factory-boy** - 测试数据工厂

## 快速开始

### 本地运行（不使用 Docker）

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

## 创建测试账号

```bash
cd backend
python manage.py create_test_users
```

## 测试账号

| 用户名 | 密码 | 角色 | 用途 |
|--------|------|------|------|
| testuser | TestPass1234 | 普通用户 | 通用测试 |
| admin | AdminPass1234 | 管理员 | 管理员功能测试 |
| runner | RunnerPass1234 | 普通用户 | CI/CD 自动化测试 |

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

项目使用 `factory-boy` 创建测试数据：

```python
from tests.factories import UserFactory

user = UserFactory()
```

## 常见问题

### 数据库连接错误

确保环境变量正确配置（示例）：

```env
DB_NAME=dungeon_toolkit
DB_USER=dungeon_toolkit
DB_PASSWORD=dungeon_toolkit
```

### ImportError

确保在 `backend/` 目录运行测试，且 Django settings 使用开发或测试配置。

## 前端回归检查（frontend-optimization-plan）

建议在本地或 dev 容器前端服务下执行以下手工回归：

- 机器人广场搜索：
  - 快速输入关键词时，请求不应按每个按键都触发。
  - 搜索与状态筛选组合时，加载/空态/错误态表现一致。
  - 快速连续切换关键词时，页面应展示最后一次输入对应结果。
- 鉴权链路：
  - access token 失效时，前端先走 refresh，再重试原请求。
  - refresh 失败时，前端清理 token 并跳转 `/login`，且无循环重试。
- 路由行为：
  - 访问 `/robots/my`、`/robots/my/bind` 应重定向到 `/profile`。
  - 首次进入未预加载页面时显示统一加载占位。
