---
alwaysApply: false
description: 编写后端代码
---
# 后端开发规范

## 技术栈
- Python 3.12 / Django 5.x / DRF
- PostgreSQL 15
- Docker 开发环境

## 项目结构
```
backend/
├── apps/
│   ├── bots/      # 机器人管理
│   └── users/     # 用户认证
├── config/        # Django 配置
└── requirements.txt
```

## 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| Model | PascalCase | `class Bot(models.Model)` |
| Serializer | `{Model}Serializer` | `BotSerializer` |
| View | `{Model}{Action}View` | `BotListView`, `BotDetailView` |
| 文件 | snake_case | `models.py`, `serializers.py` |
| 变量 | snake_case | `bot_id`, `master_qq` |

## Model 模板
```python
class MyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ... 字段
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = '名称'
        ordering = ['-created_at']
```

## 权限控制
```python
from rest_framework.permissions import AllowAny, IsAuthenticated

# 按方法区分
def get_permissions(self):
    if self.request.method == 'GET':
        return [AllowAny()]
    return [IsAuthenticated()]

# 按用户过滤
def get_queryset(self):
    return Model.objects.filter(master=self.request.user)
```

## 响应格式
```python
# 成功
return Response({'message': '操作成功'})
return Response(serializer.data, status=status.HTTP_201_CREATED)

# 错误
return Response({'detail': '资源不存在'}, status=status.HTTP_404_NOT_FOUND)
return Response({'field_name': '错误信息'}, status=status.HTTP_400_BAD_REQUEST)
```

## HTTP 状态码
```python
status.HTTP_200_OK
status.HTTP_201_CREATED
status.HTTP_400_BAD_REQUEST
status.HTTP_401_UNAUTHORIZED
status.HTTP_403_FORBIDDEN
status.HTTP_404_NOT_FOUND
```

## API 端点
```
POST /api/auth/login/
POST /api/auth/register/
GET  /api/auth/me/
GET  /api/bots/
GET  /api/bots/my/
GET  /api/bots/{id}/
POST /api/bots/bind/
POST /api/bots/{id}/regenerate-key/
DELETE /api/bots/{id}/delete/
```

## 关键规则
### 必须
- 使用 UUID 作为主键
- 所有字段添加 `verbose_name`
- 按用户过滤 queryset
- 验证所有输入

### 禁止
- 硬编码密钥（用环境变量）
- 返回未过滤的 queryset
- 跳过输入验证

## 详细规范
完整代码示例见 `backend/rules.md`