## Why

许多 DicePP 机器人运营者在私人服务器或家庭网络中部署机器人，无法获得公网 IP，导致其他玩家难以发现和使用这些机器人。建立机器人广场平台，可以让运营者登记机器人、展示功能，同时为未来的基建服务（如 Webhook 中转）打下基础。

## What Changes

- **新增用户认证系统**：支持注册/登录功能，运营者需要登录才能管理自己的机器人
- **新增机器人广场页面**：公开展示所有登记的机器人，支持搜索和筛选
- **新增机器人登记功能**：运营者登录后可登记、编辑、删除自己的机器人
- **新增机器人详情页**：展示机器人的详细信息和在线状态
- **新增运营者主页**：展示运营者拥有的所有机器人

## Capabilities

### New Capabilities

- `user-auth`: 用户注册、登录、登出、Token 认证
- `robot-registration`: 机器人登记、编辑、删除、在线状态监测
- `robot-plaza`: 机器人广场展示、搜索、筛选
- `robot-detail`: 机器人详情页展示

### Modified Capabilities

- 无（现有系统不涉及机器人相关内容）

## Impact

- **Backend**: 新增 `robots` app，处理机器人相关 CRUD；扩展 `users` app 支持 Token 认证
- **Frontend**: 新增机器人广场、登记、详情等页面
- **Database**: 新增 `Robot` 模型
- **API**: 新增 `/api/robots/` 系列接口、`/api/auth/` 接口
