## ADDED Requirements

### Requirement: 规则文档目录树展示
系统 SHALL 展示中文规则文档的层级目录树，支持折叠展开。

#### Scenario: 加载目录树
- **WHEN** 用户访问规则文档库页面
- **THEN** 系统请求 GET /api/rules/tree/，在左侧面板渲染完整的多级可折叠目录树

#### Scenario: 展开/折叠目录节点
- **WHEN** 用户点击含子节点的目录项
- **THEN** 系统展开或折叠该节点的子目录，不重新请求数据

#### Scenario: 目录树默认展开状态
- **WHEN** 目录树首次加载
- **THEN** 顶级目录默认展开，次级及以下默认折叠

---

### Requirement: 规则文档内容展示
系统 SHALL 在用户点击目录项时，在右侧内容区加载并渲染对应页面的 HTML 内容。

#### Scenario: 点击目录项加载内容
- **WHEN** 用户点击目录树中的某个叶子节点
- **THEN** 系统请求 GET /api/rules/{slug}/，在右侧内容区渲染该文档的 HTML 内容

#### Scenario: 内容页加载状态
- **WHEN** 内容正在加载时
- **THEN** 系统在内容区显示加载占位动画

#### Scenario: 内容页 URL 同步
- **WHEN** 用户切换文档页面
- **THEN** 浏览器 URL SHALL 更新为 /rules/{slug}，支持浏览器前进/后退和直接分享链接

---

### Requirement: 规则文档全文搜索
系统 SHALL 提供基于 PostgreSQL tsvector 的中文规则全文搜索功能。

#### Scenario: 搜索关键词
- **WHEN** 用户在搜索框输入关键词并提交（或停止输入300ms后自动触发）
- **THEN** 系统请求 GET /api/rules/search/?q={keyword}，展示匹配的文档标题列表（含高亮摘要）

#### Scenario: 点击搜索结果
- **WHEN** 用户点击某条搜索结果
- **THEN** 系统跳转至对应文档页面，目录树高亮对应节点

#### Scenario: 无搜索结果
- **WHEN** 搜索关键词无匹配内容
- **THEN** 系统显示"未找到相关内容"提示

#### Scenario: 搜索框清空
- **WHEN** 用户清空搜索框
- **THEN** 搜索结果列表消失，恢复正常目录树显示

---

### Requirement: CHM 源码导入
系统 SHALL 提供脚本将中文规则书的 HTML 源文件批量导入数据库。

#### Scenario: 执行导入脚本
- **WHEN** 管理员执行 python scripts/import_chm.py --ruleset dnd5e_2014 --source rules_source/玩家手册
- **THEN** 脚本解析指定目录下所有 HTML 文件（GBK 编码），将内容写入 rule_document 表，并建立正确的父子目录关系

#### Scenario: 重复导入幂等性
- **WHEN** 管理员对同一目录重复执行导入脚本
- **THEN** 脚本 MUST 使用 upsert 策略，更新已存在的文档内容而不是创建重复记录

#### Scenario: 导入后搜索索引更新
- **WHEN** 文档成功写入数据库
- **THEN** PostgreSQL tsvector 搜索向量 MUST 自动更新（通过数据库触发器维护）
