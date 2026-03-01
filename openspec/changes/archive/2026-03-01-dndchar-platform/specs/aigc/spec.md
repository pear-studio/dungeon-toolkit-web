## ADDED Requirements

### Requirement: AI 背景故事生成
系统 SHALL 根据角色信息自动生成中文背景故事，并允许用户保存或重新生成。

#### Scenario: 触发生成
- **WHEN** 已登录用户在角色详情页点击"AI 生成背景故事"按钮
- **THEN** 系统调用 POST /api/aigc/backstory/，传入角色 id，AI 根据种族/职业/背景/性格特质/理念/牵绊/缺点生成 300-500 字中文背景故事，以流式或完成后整体返回

#### Scenario: 保存生成内容
- **WHEN** 用户点击"保存"采纳 AI 生成的故事
- **THEN** 系统将内容写入角色的 ai_backstory 字段，HTTP 200

#### Scenario: 重新生成
- **WHEN** 用户点击"重新生成"
- **THEN** 系统再次调用 AI 接口，返回新的故事内容，不自动覆盖已保存内容

#### Scenario: AI 服务未配置
- **WHEN** 系统环境变量中未配置 AI_PROVIDER 或对应 API Key
- **THEN** AI 生成按钮显示为禁用状态，提示"AIGC 功能需要配置 AI 服务"

---

### Requirement: AI 角色扮演助手
系统 SHALL 提供基于角色信息的对话界面，以角色第一人称进行角色扮演对话。

#### Scenario: 发起对话
- **WHEN** 用户在角色详情页打开扮演助手面板并发送消息
- **THEN** 系统调用 POST /api/aigc/chat/，将角色完整信息注入 System Prompt，AI 以该角色第一人称回复

#### Scenario: 对话上下文保持
- **WHEN** 用户在同一会话内连续发送多条消息
- **THEN** 系统将历史对话消息一并传给 AI，保持对话连贯性

#### Scenario: 对话历史不持久化
- **WHEN** 用户关闭扮演助手面板或刷新页面
- **THEN** 对话历史清空，不存入数据库（仅存于前端内存）

---

### Requirement: 种族沉浸式描述
系统 SHALL 在角色创建向导的种族选择步骤，为每个种族展示 AI 生成的沉浸式描述文字。

#### Scenario: 展示缓存描述
- **WHEN** 用户选择某个种族
- **THEN** 系统请求 GET /api/aigc/race-lore/{slug}/，若该种族描述已缓存则直接返回，HTTP 200

#### Scenario: 首次生成并缓存
- **WHEN** 该种族描述尚未生成
- **THEN** 系统调用 AI 生成约 200 字的中文种族沉浸式描述，存入数据库缓存，后续请求直接返回缓存内容

#### Scenario: AI 服务未配置时降级
- **WHEN** AI 服务未配置
- **THEN** 系统返回该种族在规则书中的标准描述文本作为降级内容，不显示错误

---

### Requirement: AI 提供商可配置
系统 SHALL 支持通过环境变量切换 AI 提供商，不锁定特定服务商。

#### Scenario: 配置 OpenAI
- **WHEN** 环境变量 AI_PROVIDER=openai，OPENAI_API_KEY 已设置
- **THEN** 所有 AIGC 功能使用 OpenAI API 处理请求

#### Scenario: 配置自定义 Base URL
- **WHEN** 环境变量 OPENAI_BASE_URL 设置为代理地址
- **THEN** 系统使用该地址替代官方 API 地址，支持中转代理

#### Scenario: 未配置任何 AI 服务
- **WHEN** AI_PROVIDER 未设置或为空
- **THEN** 所有 AIGC 功能静默禁用，系统其他功能正常运行，不抛出错误
