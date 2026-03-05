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

## App 结构
```
app_name/
├── models.py
├── serializers.py
├── views.py
├── urls.py
└── migrations/
```

## 命名
- Model: PascalCase (`Bot`)
- Serializer: `{Model}Serializer`
- ViewSet: `{Model}ViewSet`

## API 规范
- RESTful: 复数资源名 `/api/bots/`
- 正确 HTTP 方法: GET/POST/PUT/PATCH/DELETE

## 安全
- 禁止硬编码密钥
- 使用环境变量
- API 需身份认证

## 详细规范
完整代码示例和模板见 `backend/rules.md`
