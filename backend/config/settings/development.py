from .base import *

DEBUG = True

ALLOWED_HOSTS = ['*']

# 开发环境允许所有来源的跨域请求
CORS_ALLOW_ALL_ORIGINS = True

# 开发环境数据库（可覆盖为本地连接）
DATABASES['default']['HOST'] = config('DB_HOST', default='localhost')
