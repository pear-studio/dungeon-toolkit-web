# 命令速查

## 说明

- 默认使用 `docker compose`（Compose v2）
- 如果你的环境仅支持 `docker-compose`，请将下方命令整体替换
- 命令均在项目根目录执行：`dungeon-toolkit-web/`

---

## 开发环境

```bash
# 启动开发环境
docker compose -f docker-compose.dev.yml up -d --build

# 查看状态
docker compose -f docker-compose.dev.yml ps

# 查看日志
docker compose -f docker-compose.dev.yml logs -f

# 停止开发环境
docker compose -f docker-compose.dev.yml down
```

## 常用服务命令

```bash
# 后端迁移
docker compose -f docker-compose.dev.yml exec backend python manage.py migrate

# 创建测试用户
docker compose -f docker-compose.dev.yml exec backend python manage.py create_test_users

# 进入后端容器
docker compose -f docker-compose.dev.yml exec backend bash

# 进入前端容器
docker compose -f docker-compose.dev.yml exec frontend sh
```

## 测试与检查

```bash
# 后端测试
docker compose -f docker-compose.dev.yml exec backend pytest

# 前端 lint
docker compose -f docker-compose.dev.yml exec frontend npm run lint

# 前端构建（验证路由懒加载与产物可构建）
docker compose -f docker-compose.dev.yml exec frontend npm run build

# 本地（不进容器）后端测试
cd backend && pytest
```

## 脚本入口

```bash
bash scripts/dev.sh start
bash scripts/dev.sh stop
bash scripts/dev.sh status
bash scripts/dev.sh rebuild
bash scripts/dev.sh test
bash scripts/dev.sh lint
bash scripts/dev.sh check
```

## 测试环境（隔离）

```bash
# 启动测试环境
docker compose -f docker-compose.test.yml up -d --build

# 运行测试
docker compose -f docker-compose.test.yml exec backend-test pytest
```

## 生产部署常用命令

```bash
# 构建并启动
docker compose up -d --build

# 查看状态
docker compose ps

# 查看后端日志
docker compose logs -f backend

# 重启后端
docker compose restart backend

# 停止服务
docker compose down
```
