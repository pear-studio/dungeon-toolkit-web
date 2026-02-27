# 后端开发规范

## 技术栈

- Python 3.x
- Django 5.x
- Django REST Framework (DRF)
- PostgreSQL

---

## 项目结构

```
backend/
├── apps/                 # Django 应用
│   ├── gamedata/        # 游戏数据（种族、职业、法术等）
│   ├── characters/      # 角色管理
│   ├── users/           # 用户认证
│   ├── rules/           # 规则相关
│   └── aigc/           # AI 生成内容
├── config/              # Django 配置
│   ├── settings/       # settings 模块
│   ├── urls.py         # 主 URL 配置
│   └── wsgi.py         # WSGI 入口
├── data/                # 静态数据
│   ├── dnd5e_2014/     # D&D 5e 2014 版数据
│   ├── parsers/        # 数据解析脚本
│   └── shared/         # 共享数据
├── scripts/            # 工具脚本
└── requirements.txt    # 依赖
```

---

## App 结构规范

每个 Django app 应包含以下文件：

```
app_name/
├── __init__.py
├── apps.py
├── models.py
├── serializers.py
├── views.py
├── urls.py
└── migrations/
    └── __init__.py
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| Model | PascalCase | `class Character(Model):` |
| Serializer | PascalCase + Serializer | `class CharacterSerializer(ModelSerializer):` |
| ViewSet | PascalCase + ViewSet | `class CharacterViewSet(ModelViewSet):` |
| URL | snake_case | `urlpatterns` |

---

## 数据模型规范

### Model 定义

```python
class Character(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    level = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']
        indexes = [
            models.Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name
```

### Serializer 定义

```python
class CharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Character
        fields = ['id', 'name', 'slug', 'level', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
```

---

## 数据生成规范

### 禁止行为

| 行为 | 说明 |
|------|------|
| 直接修改 JSON 数据 | 必须使用 `backend/data/parsers/` 下的解析脚本 |
| 跳过 rules_source 直接写 JSON | 无法溯源 |
| 凭记忆生成规则数据 | AI 生成的细节极易出错 |

### 数据流向

```
rules_source/DND5e_chm/        # 原始 HTML 数据
        ↓  (parsers/*.py)
backend/data/dnd5e_2014/*.json # JSON 数据
        ↓  (scripts/import_gamedata.py)
PostgreSQL 数据库
        ↓  (DRF API)
前端 gamedataStore
```

---

## API 设计规范

### RESTful 原则

- 资源命名使用复数形式：`/api/characters/`
- 使用正确的 HTTP 方法：
  - `GET` - 获取资源列表
  - `GET /{id}/` - 获取单个资源
  - `POST` - 创建资源
  - `PUT/PATCH` - 更新资源
  - `DELETE` - 删除资源

### 响应格式

```json
{
  "id": 1,
  "name": "角色名",
  "slug": "character-name"
}
```

---

## 安全规范

- 禁止在代码中硬编码密钥/密码
- 使用环境变量存储敏感配置
- 所有 API 需要身份认证（除公开资源外）
- 验证用户输入，防止 SQL 注入

---

## 相关规范

- 规则数据来源：[`docs/conventions/data-sources.md`](../docs/conventions/data-sources.md)
- 部署配置：[`docs/deployment.md`](../docs/deployment.md)
