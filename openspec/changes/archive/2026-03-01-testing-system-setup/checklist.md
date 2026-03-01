# 测试体系建设 - 检查清单

## C1. 环境配置检查

### C1.1 依赖安装
- [ ] `pytest` 已安装且版本 >= 7.0
- [ ] `pytest-django` 已安装且版本 >= 4.5
- [ ] `pytest-cov` 已安装且版本 >= 4.1
- [ ] `factory-boy` 已安装且版本 >= 3.3
- [ ] `pytest-mock` 已安装且版本 >= 3.12
- [ ] 运行 `pip list | grep pytest` 确认安装

### C1.2 pytest 配置
- [ ] `backend/pytest.ini` 文件存在且配置正确
- [ ] `backend/conftest.py` 文件存在且包含基础 fixtures
- [ ] `DJANGO_SETTINGS_MODULE` 在 pytest.ini 中正确设置

---

## C2. 目录结构检查

### C2.1 测试目录
- [ ] `backend/apps/users/tests/` 目录存在
- [ ] `backend/apps/characters/tests/` 目录存在
- [ ] `backend/apps/gamedata/tests/` 目录存在
- [ ] `backend/tests/` 目录存在

### C2.2 测试文件
- [ ] `backend/apps/users/tests/__init__.py` 存在
- [ ] `backend/apps/characters/tests/__init__.py` 存在
- [ ] `backend/apps/gamedata/tests/__init__.py` 存在
- [ ] `backend/tests/__init__.py` 存在

---

## C3. 测试工厂检查

### C3.1 工厂定义
- [ ] `backend/tests/factories.py` 存在
- [ ] `UserFactory` 正确定义且继承 DjangoModelFactory
- [ ] `CharacterFactory` 正确定义
- [ ] `RaceFactory` 正确定义 (如需要)
- [ ] `CharClassFactory` 正确定义 (如需要)
- [ ] `BackgroundFactory` 正确定义 (如需要)

### C3.2 工厂使用
- [ ] factories.py 中每个 factory 的 Meta.model 正确
- [ ] factory 的字段定义与 model 一致

---

## C4. 单元测试检查

### C4.1 Users App
- [ ] `apps/users/tests/test_models.py` 存在
- [ ] `apps/users/tests/test_serializers.py` 存在
- [ ] `apps/users/tests/test_views.py` 存在

### C4.2 Characters App
- [ ] `apps/characters/tests/test_models.py` 存在
- [ ] `apps/characters/tests/test_serializers.py` 存在
- [ ] `apps/characters/tests/test_views.py` 存在

### C4.3 Gamedata App
- [ ] `apps/gamedata/tests/test_views.py` 存在

### C4.4 测试内容
- [ ] 每个测试文件包含有意义的测试用例
- [ ] 测试用例使用 `@pytest.mark.django_db` 或 `db` fixture
- [ ] 测试用例使用 factory 创建测试数据
- [ ] 断言清晰，测试意图明确

---

## C5. 测试账号检查

### C5.1 Command 文件
- [ ] `apps/users/management/__init__.py` 存在
- [ ] `apps/users/management/commands/__init__.py` 存在
- [ ] `apps/users/management/commands/create_test_users.py` 存在
- [ ] command 继承 `BaseCommand`
- [ ] command 包含 `handle` 方法

### C5.2 Command 功能
- [ ] command 可正常执行 `python manage.py create_test_users`
- [ ] 创建以下测试账号:
  - `testuser` (test@dungeon-toolkit.local / TestPass1234)
  - `admin` (admin@dungeon-toolkit.local / AdminPass1234)
  - `runner` (runner@dungeon-toolkit.local / RunnerPass1234)
- [ ] 已存在账号不会被重复创建 (使用 get_or_create)

### C5.3 测试账号可用性
- [ ] 使用 testuser 账号可登录系统
- [ ] 使用 admin 账号可登录系统并访问 /admin
- [ ] 测试账号密码符合安全要求 (非弱密码)

---

## C6. 测试运行检查

### C6.1 本地运行
- [ ] `pytest` 命令可正常执行
- [ ] 无配置错误或导入错误
- [ ] 测试用例可被发现 (test_*.py 模式)
- [ ] 测试结果输出清晰

### C6.2 测试结果
- [ ] 所有测试用例通过 (PASSED)
- [ ] 无失败的测试用例 (FAILED)
- [ ] 无跳过的测试 (SKIPPED) - 除非有充分理由

### C6.3 覆盖率
- [ ] 可运行 `pytest --cov` 命令
- [ ] 覆盖率报告生成成功
- [ ] 核心模块覆盖率 >= 70%

---

## C7. 代码质量检查

### C7.1 测试代码质量
- [ ] 测试函数命名清晰 (test_功能_预期行为)
- [ ] 测试类命名清晰 (Test模块名)
- [ ] 包含必要的 docstring 说明测试目的
- [ ] 测试之间相互独立
- [ ] 无硬编码的测试数据 (使用 factory)

### C7.2 配置文件质量
- [ ] `pytest.ini` 配置规范
- [ ] 无敏感信息泄露 (密码等)
- [ ] `.gitignore` 包含测试生成的文件

---

## C8. 文档检查

### C8.1 测试文档
- [ ] `docs/testing.md` 存在且包含:
  - 测试运行方法
  - 测试账号信息
  - 测试覆盖范围说明
- [ ] `README.md` 更新了测试相关说明

### C8.2 文档内容
- [ ] 测试账号信息准确
- [ ] 运行命令正确
- [ ] 故障排除指南 (如有)

---

## C9. 集成检查 (可选)

### C9.1 Docker 环境
- [ ] 在 Docker 环境中 pytest 可运行
- [ ] 数据库连接配置正确

### C9.2 CI/CD (如配置)
- [ ] CI 配置文件存在 (如 `.github/workflows/test.yml`)
- [ ] CI 测试通过

---

## 验收签字

| 检查项 | 状态 | 检查人 | 日期 |
|--------|------|--------|------|
| 环境配置 | ⬜ | | |
| 目录结构 | ⬜ | | |
| 测试工厂 | ⬜ | | |
| 单元测试 | ⬜ | | |
| 测试账号 | ⬜ | | |
| 测试运行 | ⬜ | | |
| 代码质量 | ⬜ | | |
| 文档 | ⬜ | | |

---

## 快速验证命令

```bash
# 1. 检查 pytest 安装
pip list | grep pytest

# 2. 检查配置文件
ls -la backend/pytest.ini backend/conftest.py

# 3. 检查测试目录
find backend -type d -name tests

# 4. 运行测试
cd backend && pytest -v

# 5. 运行测试并查看覆盖率
cd backend && pytest --cov=. --cov-report=term-missing

# 6. 创建测试账号
cd backend && python manage.py create_test_users
```
