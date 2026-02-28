# 测试指南

## 概述

本文档介绍 Dungeon Toolkit Web 项目的测试体系，包括如何运行测试、使用测试账号等。

## 测试框架

- **pytest** - Python 主流测试框架
- **pytest-django** - Django 集成
- **factory-boy** - 测试数据工厂

## 快速开始

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行指定应用的测试
pytest apps/users/
pytest apps/characters/
pytest apps/gamedata/

# 运行带覆盖率报告
pytest --cov=. --cov-report=html
```

### 创建测试账号

```bash
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
├── pytest.ini              # pytest 配置
├── conftest.py            # 全局 fixtures
├── tests/
│   ├── __init__.py
│   └── factories.py        # 测试数据工厂
└── apps/
    ├── users/
    │   └── tests/
    │       ├── test_models.py
    │       ├── test_serializers.py
    │       └── test_views.py
    ├── characters/
    │   └── tests/
    │       ├── test_models.py
    │       ├── test_serializers.py
    │       └── test_views.py
    └── gamedata/
        └── tests/
            └── test_views.py
```

## 测试数据工厂

项目使用 `factory-boy` 创建测试数据：

```python
from tests.factories import UserFactory, CharacterFactory, RaceFactory

# 创建用户
user = UserFactory()

# 创建角色
character = CharacterFactory(owner=user)

# 创建游戏数据
race = RaceFactory()
```

## 在 Docker 中运行测试

```bash
# 启动开发环境
docker-compose -f docker-compose.dev.yml up -d

# 进入后端容器
docker-compose exec backend bash

# 运行测试
python manage.py test
# 或
pytest
```

## 测试覆盖范围

### Users App
- User 模型创建与验证
- 注册/登录序列化器
- 认证视图

### Characters App
- Character 模型与字段验证
- CRUD 序列化器
- 角色管理视图与权限

### Gamedata App
- 游戏数据查询 API
- 过滤与分页

## 常见问题

### 数据库错误

确保环境变量正确配置：
```
DB_NAME=dungeon_toolkit
DB_USER=dungeon_user
DB_PASSWORD=your_password
```

### ImportError

确保在正确的目录运行测试，且 Django settings 配置正确。
