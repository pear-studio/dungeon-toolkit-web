# 测试体系建设规格说明

## 1. 项目概述

### 1.1 变更名称
测试体系建设 - 引入单元测试与测试账号

### 1.2 变更类型
基础设施/质量保障

### 1.3 核心目标
为 Dungeon Toolkit Web 项目建立完整的测试体系，包括后端单元测试框架、测试账号管理机制，确保代码质量和人工测试便利性。

### 1.4 适用范围
- 后端 Django API 单元测试
- 前端组件测试 (可选)
- 人工测试账号管理

---

## 2. 现状分析

### 2.1 当前测试状态
| 类别 | 现状 | 说明 |
|------|------|------|
| 后端单元测试 | ❌ 无 | 未配置 pytest |
| 后端集成测试 | ⚠️ 基础 | 仅有 `unittest/test_api.py` 手动脚本 |
| 前端测试 | ❌ 无 | 未配置任何测试框架 |
| 测试账号 | ⚠️ 手动 | 需手动注册或修改代码创建 |

### 2.2 现有测试文件
- `unittest/test_api.py` - Python 集成测试脚本，直接调用 HTTP API

### 2.3 依赖环境
- Python 3.11+
- Node.js 20+
- PostgreSQL 15
- Docker & Docker Compose

---

## 3. 规格说明

### 3.1 后端测试框架

#### 3.1.1 技术选型
| 组件 | 选型 | 版本 | 说明 |
|------|------|------|------|
| 测试框架 | pytest | >=7.0 | Python 主流测试框架 |
| Django 集成 | pytest-django | >=4.5 | Django 专用插件 |
| 测试工厂 | factory-boy | >=3.3 | 替代 fixtures 的工厂模式 |
| 断言库 | pytest-mock | >=3.12 | Mock 功能增强 |
| 覆盖率 | pytest-cov | >=4.1 | 代码覆盖率 |

#### 3.1.2 目录结构
```
backend/
├── pytest.ini                 # pytest 配置
├── conftest.py               # 全局 fixtures
├── apps/
│   ├── users/
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_serializers.py
│   │       └── test_views.py
│   ├── characters/
│   │   └── tests/
│   │       ├── __init__.py
│   │       ├── test_models.py
│   │       ├── test_serializers.py
│   │       └── test_views.py
│   └── gamedata/
│       └── tests/
│           ├── __init__.py
│           └── test_views.py
└── tests/
    ├── __init__.py
    └── test_utils.py         # 通用测试工具
```

#### 3.1.3 pytest.ini 配置
```ini
[pytest]
DJANGO_SETTINGS_MODULE = config.settings.development
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short --strict-markers
testpaths = apps tests
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    unit: marks tests as unit tests
filterwarnings =
    ignore::DeprecationWarning
```

#### 3.1.4 conftest.py 全局配置
```python
import pytest
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def user(db):
    """创建测试用户"""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='TestPass123'
    )

@pytest.fixture
def api_client():
    """DRF API 客户端"""
    from rest_framework.test import APIClient
    return APIClient()

@pytest.fixture
def authenticated_client(api_client, user):
    """已认证的 API 客户端"""
    api_client.force_authenticate(user=user)
    return api_client
```

### 3.2 测试账号管理

#### 3.2.1 测试账号配置
| 账号用途 | 用户名 | 邮箱 | 密码 | 说明 |
|----------|--------|------|------|------|
| 人工测试 | testuser | test@dungeon-toolkit.local | TestPass1234 | 通用测试账号 |
| 管理员测试 | admin | admin@dungeon-toolkit.local | AdminPass1234 | 管理员权限 |
| API 自动化 | runner | runner@dungeon-toolkit.local | RunnerPass1234 | CI/CD 使用 |

#### 3.2.2 测试账号创建方式
采用 Django management command 方式初始化测试账号：

```python
# backend/apps/users/management/commands/create_test_users.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = '创建测试账号'

    def handle(self, *args, **options):
        users = [
            {'username': 'testuser', 'email': 'test@dungeon-toolkit.local', 
             'password': 'TestPass1234', 'is_staff': False},
            {'username': 'admin', 'email': 'admin@dungeon-toolkit.local',
             'password': 'AdminPass1234', 'is_staff': True, 'is_superuser': True},
            {'username': 'runner', 'email': 'runner@dungeon-toolkit.local',
             'password': 'RunnerPass1234', 'is_staff': False},
        ]
        
        for u in users:
            user, created = User.objects.get_or_create(username=u['username'])
            user.email = u['email']
            user.set_password(u['password'])
            user.is_staff = u.get('is_staff', False)
            user.is_superuser = u.get('is_superuser', False)
            user.save()
            
            status = '创建' if created else '更新'
            self.stdout.write(f'{status}: {u["username"]}')
```

#### 3.2.3 测试数据 fixtures
创建基础测试数据工厂：

```python
# backend/tests/factories.py
import factory
from factory.django import DjangoModelFactory
from apps.users.models import User
from apps.characters.models import Character

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    
    username = factory.Sequence(lambda n: f'user_{n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.username}@example.com')
    password = factory.PostGenerationMethodCall('set_password', 'password123')

class CharacterFactory(DjangoModelFactory):
    class Meta:
        model = Character
    
    owner = factory.SubFactory(UserFactory)
    name = factory.Sequence(lambda n: f'Character_{n}')
    race_slug = 'human'
    class_slug = 'wizard'
    background_slug = 'sage'
    ruleset_slug = 'dnd5e_2014'
    level = 1
```

### 3.3 单元测试覆盖要求

#### 3.3.1 Users App 测试覆盖
| 模块 | 测试内容 | 优先级 |
|------|----------|--------|
| Models | User 创建、字段验证、权限方法 | 高 |
| Serializers | 注册序列化、登录序列化、字段校验 | 高 |
| Views | 注册、登录、获取用户信息、权限验证 | 高 |

#### 3.3.2 Characters App 测试覆盖
| 模块 | 测试内容 | 优先级 |
|------|----------|--------|
| Models | Character 创建、字段验证、默认值 | 高 |
| Serializers | 角色创建/更新序列化、字段校验 | 高 |
| Views | CRUD 操作、权限隔离、分享功能 | 高 |

#### 3.3.3 Gamedata App 测试覆盖
| 模块 | 测试内容 | 优先级 |
|------|----------|--------|
| Views | 种族/职业/背景/法术列表查询 | 中 |
| Serializers | 数据序列化输出 | 中 |

### 3.4 前端测试 (可选)

#### 3.4.1 技术选型
| 组件 | 选型 | 说明 |
|------|------|------|
| 测试框架 | Vitest | Vite 官方推荐，与 Vite 集成良好 |
| 组件测试 | React Testing Library | React 官方推荐 |
| 断言 | expect (Vitest 内置) | Jest 风格 API |
| Mock | Vitest Mocks | HTTP 请求模拟 |

#### 3.4.2 目录结构
```
frontend/src/
├── components/
│   └── __tests__/
│       ├── ProtectedRoute.test.tsx
│       └── CharacterCard.test.tsx
├── stores/
│   └── __tests__/
│       ├── authStore.test.ts
│       └── characterStore.test.ts
└── lib/
    └── __tests__/
        └── api.test.ts
```

---

## 4. 实施步骤

### 4.1 依赖安装
```bash
# 后端
pip install pytest pytest-django pytest-cov factory-boy pytest-mock

# 前端 (可选)
npm install -D vitest @testing-library/react @testing-library/jest-dom jsdom
```

### 4.2 测试数据初始化
```bash
# 创建测试账号
python manage.py create_test_users

# 运行单元测试
pytest

# 生成覆盖率报告
pytest --cov=. --cov-report=html
```

### 4.3 CI 集成 (可选)
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-django pytest-cov
      - name: Run tests
        env:
          DB_PASSWORD: test
        run: pytest --cov=. --cov-report=xml
```

---

## 5. 验收标准

### 5.1 功能验收
- [ ] pytest 配置正确，可运行 `pytest` 命令
- [ ] 单元测试覆盖 users app 核心功能
- [ ] 单元测试覆盖 characters app 核心功能
- [ ] 测试账号可通过 command 创建
- [ ] 测试账号可在人工测试中使用

### 5.2 质量验收
- [ ] 测试用例命名清晰，符合规范
- [ ] 测试之间相互独立，不依赖执行顺序
- [ ] 每个 model 有对应的 factory
- [ ] 测试通过率 100%

### 5.3 文档验收
- [ ] README 更新测试运行说明
- [ ] 测试账号信息记录在文档中

---

## 6. 风险与限制

### 6.1 已知风险
- 集成测试覆盖需要真实数据库连接
- 前端测试为可选，项目初期可暂不实施
- CI/CD 集成需要仓库配置权限

### 6.2 实施限制
- 依赖 Docker 环境运行完整测试
- Windows 环境下 pytest 配置需调整
- 测试数据 factory 需要与 model 同步更新
