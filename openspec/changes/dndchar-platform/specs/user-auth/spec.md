## ADDED Requirements

### Requirement: 用户注册
系统 SHALL 允许用户通过邮箱和密码创建账号。

#### Scenario: 注册成功
- **WHEN** 用户提交有效的邮箱、用户名和密码（密码至少8位）
- **THEN** 系统创建账号，返回 JWT access token 和 refresh token，HTTP 201

#### Scenario: 邮箱已存在
- **WHEN** 用户提交的邮箱已被注册
- **THEN** 系统返回 HTTP 400，错误信息说明邮箱已被使用

#### Scenario: 密码强度不足
- **WHEN** 用户提交的密码少于8位
- **THEN** 系统返回 HTTP 400，错误信息说明密码要求

---

### Requirement: 用户登录
系统 SHALL 允许用户通过邮箱和密码登录，返回 JWT Token。

#### Scenario: 登录成功
- **WHEN** 用户提交正确的邮箱和密码
- **THEN** 系统返回 HTTP 200，包含 access token（有效期1小时）和 refresh token（有效期7天）

#### Scenario: 凭证错误
- **WHEN** 用户提交错误的邮箱或密码
- **THEN** 系统返回 HTTP 401，不透露是邮箱还是密码错误

#### Scenario: 账号不存在
- **WHEN** 用户提交未注册的邮箱
- **THEN** 系统返回 HTTP 401，提示凭证无效

---

### Requirement: JWT Token 刷新
系统 SHALL 允许客户端使用 refresh token 换取新的 access token。

#### Scenario: 刷新成功
- **WHEN** 客户端提交有效且未过期的 refresh token
- **THEN** 系统返回新的 access token，HTTP 200

#### Scenario: Refresh Token 过期
- **WHEN** 客户端提交已过期的 refresh token
- **THEN** 系统返回 HTTP 401，客户端需重新登录

---

### Requirement: 获取当前用户信息
系统 SHALL 允许已登录用户获取自己的账号信息。

#### Scenario: 获取成功
- **WHEN** 已登录用户请求 GET /api/auth/me/
- **THEN** 系统返回用户 id、email、username、created_at，HTTP 200

#### Scenario: 未登录访问
- **WHEN** 未携带有效 Token 的请求访问 /api/auth/me/
- **THEN** 系统返回 HTTP 401

---

### Requirement: 受保护路由鉴权
系统 SHALL 对所有需要登录的 API 进行 JWT 鉴权，拒绝未授权访问。

#### Scenario: 有效 Token 访问
- **WHEN** 请求携带有效的 access token（Header: Authorization: Bearer <token>）
- **THEN** 系统正常处理请求

#### Scenario: 无效 Token 访问
- **WHEN** 请求携带无效或篡改的 token
- **THEN** 系统返回 HTTP 401，拒绝访问
