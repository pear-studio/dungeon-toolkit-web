# 后端开发规范

## 项目架构

```
backend/
├── apps/              # Django 应用
│   ├── bots/          # 机器人管理
│   └── users/         # 用户认证
├── config/            # Django 配置
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── requirements.txt
```

## App 结构

```
app_name/
├── models.py          # 数据模型
├── serializers.py     # DRF 序列化器
├── views.py           # 视图/ViewSet
├── urls.py            # 路由
├── authentication.py  # 自定义认证（如需要）
└── migrations/        # 数据库迁移
```

## Model 规范

### 基础字段模板

```python
class MyModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ... 业务字段
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')

    class Meta:
        verbose_name = '模型名'
        verbose_name_plural = '模型名'
        ordering = ['-created_at']

    def __str__(self):
        return self.name
```

### 状态选项

```python
STATUS_CHOICES = [
    ('online', '在线'),
    ('offline', '离线'),
]
status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='offline')
```

## Serializer 规范

```python
class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
```

## View 规范

### 使用 Generic Views

```python
# 列表 + 创建
class MyModelListView(generics.ListCreateAPIView):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer

# 详情
class MyModelDetailView(generics.RetrieveAPIView):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    lookup_field = 'id'

# 更新
class MyModelUpdateView(generics.UpdateAPIView):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return MyModel.objects.filter(owner=self.request.user)

# 删除
class MyModelDeleteView(generics.DestroyAPIView):
    queryset = MyModel.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
```

### 自定义 APIView

```python
class MyCustomView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # 验证输入
        if not request.data.get('field'):
            return Response(
                {'field': '此字段必填'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # 处理逻辑
        # ...
        
        return Response({'message': '成功'})
```

## 权限控制

```python
from rest_framework.permissions import AllowAny, IsAuthenticated

# 公开访问
permission_classes = [AllowAny]

# 需要登录
permission_classes = [IsAuthenticated]

# 按方法区分
def get_permissions(self):
    if self.request.method == 'GET':
        return [AllowAny()]
    return [IsAuthenticated()]
```

## URL 规范

```python
# apps/myapp/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.MyModelListView.as_view(), name='list'),
    path('<uuid:id>/', views.MyModelDetailView.as_view(), name='detail'),
    path('<uuid:id>/update/', views.MyModelUpdateView.as_view(), name='update'),
    path('<uuid:id>/delete/', views.MyModelDeleteView.as_view(), name='delete'),
]
```

## 响应格式

### 成功响应

```python
# 单个对象
return Response(serializer.data)

# 创建成功
return Response(data, status=status.HTTP_201_CREATED)

# 操作成功
return Response({'message': '操作成功'})
```

### 错误响应

```python
# 验证错误
return Response(
    {'field_name': '错误信息'},
    status=status.HTTP_400_BAD_REQUEST
)

# 未找到
return Response(
    {'detail': '资源不存在'},
    status=status.HTTP_404_NOT_FOUND
)

# 无权限
return Response(
    {'detail': '无权限访问'},
    status=status.HTTP_403_FORBIDDEN
)
```

## 常见错误

### ❌ 忘记过滤用户数据

```python
# 错误：返回所有数据
def get_queryset(self):
    return MyModel.objects.all()

# 正确：只返回当前用户数据
def get_queryset(self):
    return MyModel.objects.filter(owner=self.request.user)
```

### ❌ 硬编码敏感信息

```python
# 错误
SECRET_KEY = 'my-secret-key'

# 正确
SECRET_KEY = os.environ.get('SECRET_KEY')
```

### ❌ 缺少输入验证

```python
# 错误：直接使用未验证数据
bot_id = request.data['bot_id']

# 正确：先验证
bot_id = request.data.get('bot_id')
if not bot_id:
    return Response({'bot_id': '必填'}, status=400)
```

## 依赖说明

| 包 | 用途 |
|----|------|
| `django` | Web 框架 |
| `djangorestframework` | REST API |
| `psycopg2-binary` | PostgreSQL 驱动 |
| `gunicorn` | WSGI 服务器 |
| `django-cors-headers` | CORS 支持 |