# 测试体系建设 - 任务清单

## 阶段一: 基础设施搭建

### T1.1 安装测试依赖
- [ ] **T1.1.1** 在 `backend/requirements.txt` 中添加测试依赖
  - pytest>=7.0
  - pytest-django>=4.5
  - pytest-cov>=4.1
  - factory-boy>=3.3
  - pytest-mock>=3.12

- [ ] **T1.1.2** 安装依赖: `pip install -r requirements.txt`

### T1.2 配置 pytest
- [ ] **T1.2.1** 创建 `backend/pytest.ini` 配置文件
- [ ] **T1.2.2** 创建 `backend/conftest.py` 全局 fixtures
- [ ] **T1.2.3** 更新 `backend/config/settings/development.py` 添加测试配置

## 阶段二: 测试框架搭建

### T2.1 创建测试目录结构
- [ ] **T2.1.1** 创建 `backend/apps/users/tests/` 目录和 `__init__.py`
- [ ] **T2.1.2** 创建 `backend/apps/characters/tests/` 目录和 `__init__.py`
- [ ] **T2.1.3** 创建 `backend/apps/gamedata/tests/` 目录和 `__init__.py`
- [ ] **T2.1.4** 创建 `backend/tests/` 目录和 `__init__.py`

### T2.2 创建测试工厂
- [ ] **T2.2.1** 创建 `backend/tests/factories.py` 包含 UserFactory
- [ ] **T2.2.2** 在 factories.py 添加 CharacterFactory
- [ ] **T2.2.3** 在 factories.py 添加其他模型工厂 (Race, CharClass, Background)

## 阶段三: 单元测试编写

### T3.1 Users App 测试
- [ ] **T3.1.1** 编写 `apps/users/tests/test_models.py` - User 模型测试
- [ ] **T3.1.2** 编写 `apps/users/tests/test_serializers.py` - 序列化器测试
- [ ] **T3.1.3** 编写 `apps/users/tests/test_views.py` - 视图测试

### T3.2 Characters App 测试
- [ ] **T3.2.1** 编写 `apps/characters/tests/test_models.py` - Character 模型测试
- [ ] **T3.2.2** 编写 `apps/characters/tests/test_serializers.py` - 序列化器测试
- [ ] **T3.2.3** 编写 `apps/characters/tests/test_views.py` - 视图测试

### T3.3 Gamedata App 测试
- [ ] **T3.3.1** 编写 `apps/gamedata/tests/test_views.py` - API 视图测试

## 阶段四: 测试账号管理

### T4.1 创建测试账号 Command
- [ ] **T4.1.1** 创建 `apps/users/management/__init__.py`
- [ ] **T4.1.2** 创建 `apps/users/management/commands/__init__.py`
- [ ] **T4.1.3** 创建 `apps/users/management/commands/create_test_users.py`

### T4.2 测试账号配置
- [ ] **T4.2.1** 运行 command 创建测试账号
- [ ] **T4.2.2** 验证测试账号可正常登录
- [ ] **T4.2.3** 记录测试账号信息到 `docs/testing.md`

## 阶段五: 测试验证

### T5.1 运行测试
- [ ] **T5.1.1** 运行 `pytest` 验证基础配置
- [ ] **T5.1.2** 修复测试中的问题
- [ ] **T5.1.3** 确保所有测试通过

### T5.2 覆盖率报告
- [ ] **T5.2.1** 运行 `pytest --cov` 生成覆盖率报告
- [ ] **T5.2.2** 确认覆盖率达标 (目标: >70%)

## 阶段六: 文档更新

### T6.1 更新项目文档
- [ ] **T6.1.1** 创建 `docs/testing.md` 测试指南
- [ ] **T6.1.2** 更新 `README.md` 添加测试运行说明
- [ ] **T6.1.3** 在 `.gitignore` 中忽略 `htmlcov/` 目录

---

## 任务依赖关系

```
T1.1 ──┬──► T1.2 ──┬──► T2.1 ──┬──► T3.1
       │           │           │
       │           │           ├──► T3.2
       │           │           │
       │           │           └──► T3.3
       │           │
       │           └──► T2.2 ──┬──► T3.1
       │                       ├──► T3.2
       │                       └──► T3.3
       │
       └──► T4.1 ──► T4.2 ──► T5.1 ──► T5.2 ──► T6.1
```

## 关键里程碑

| 里程碑 | 描述 | 完成标准 |
|--------|------|----------|
| M1 | 基础设施完成 | pytest 可运行，无配置错误 |
| M2 | 单元测试完成 | users/characters 核心功能测试覆盖 |
| M3 | 测试账号可用 | 人工测试可使用测试账号登录 |
| M4 | 全部完成 | 所有测试通过，文档齐全 |
