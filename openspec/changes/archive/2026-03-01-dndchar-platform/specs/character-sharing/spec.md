## ADDED Requirements

### Requirement: 开启/关闭角色公开分享
系统 SHALL 允许角色所有者为角色生成唯一的公开分享链接，并可随时关闭分享。

#### Scenario: 开启公开分享
- **WHEN** 角色所有者调用 POST /api/characters/{id}/share/，请求体 { "is_public": true }
- **THEN** 系统将角色 is_public 设为 true，生成唯一的 share_token（若不存在），返回完整的分享 URL，HTTP 200

#### Scenario: 关闭公开分享
- **WHEN** 角色所有者调用 POST /api/characters/{id}/share/，请求体 { "is_public": false }
- **THEN** 系统将角色 is_public 设为 false，原 share_token 保持不变（再次开启时可复用），HTTP 200

#### Scenario: share_token 唯一性
- **WHEN** 系统生成 share_token
- **THEN** share_token MUST 为全局唯一的随机字符串（UUID 或等效随机串），不可被枚举猜测

---

### Requirement: 公开角色卡访问
系统 SHALL 允许任何人（包括未登录用户）通过分享链接访问公开角色卡。

#### Scenario: 访问公开角色卡
- **WHEN** 任何人（含未登录用户）访问 /share/{token}
- **THEN** 系统展示该角色的完整只读角色卡，包含所有非私密信息

#### Scenario: 访问已关闭分享的角色
- **WHEN** 用户访问 is_public=false 的角色的分享链接
- **THEN** 系统返回 HTTP 404，页面提示"该角色未公开或链接已失效"

#### Scenario: 访问不存在的分享链接
- **WHEN** 用户访问不存在的 share_token
- **THEN** 系统返回 HTTP 404

---

### Requirement: 公开分享页只读保护
系统 SHALL 确保公开分享页不提供任何编辑功能。

#### Scenario: 分享页无编辑入口
- **WHEN** 任何用户（含角色所有者）通过分享链接访问角色卡
- **THEN** 页面 MUST 不显示编辑、删除等操作按钮

#### Scenario: 所有者访问自己的分享页
- **WHEN** 已登录的角色所有者通过分享链接访问
- **THEN** 系统展示只读角色卡，并提供"前往编辑"的链接，跳转到正常编辑页
