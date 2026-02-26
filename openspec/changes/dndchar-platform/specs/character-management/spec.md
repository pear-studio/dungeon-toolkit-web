## ADDED Requirements

### Requirement: 角色列表展示
系统 SHALL 为已登录用户展示其名下所有角色的列表。

#### Scenario: 展示角色卡片网格
- **WHEN** 已登录用户访问角色列表页
- **THEN** 系统展示该用户所有角色的卡片（含角色名、种族、职业、等级、最后修改时间），按更新时间倒序排列

#### Scenario: 无角色时展示引导
- **WHEN** 用户尚未创建任何角色
- **THEN** 系统展示空状态页面，提供"创建第一个角色"的引导按钮

---

### Requirement: 角色详情查看
系统 SHALL 展示角色的完整信息，包含所有属性、技能、法术、物品栏等。

#### Scenario: 展示角色卡
- **WHEN** 用户访问自己的角色详情页
- **THEN** 系统展示完整角色卡，包含：基础信息、六维属性及修正值、熟练加值、技能列表、豁免、战斗属性（AC/HP/速度）、物品栏、法术（若有）、背景故事

#### Scenario: 访问他人角色（未公开）
- **WHEN** 用户尝试访问非自己且未公开的角色详情
- **THEN** 系统返回 HTTP 403，拒绝访问

---

### Requirement: 角色信息编辑
系统 SHALL 允许角色所有者编辑角色的各项信息。

#### Scenario: 编辑基础属性
- **WHEN** 角色所有者修改角色的 HP、AC、属性值、物品栏等字段并保存
- **THEN** 系统更新角色记录，返回 HTTP 200，页面显示更新后的数据

#### Scenario: 编辑背景故事
- **WHEN** 角色所有者在富文本区域编辑背景故事/性格特质/理念/牵绊/缺点并保存
- **THEN** 系统保存文本内容，HTTP 200

#### Scenario: 非所有者尝试编辑
- **WHEN** 非角色所有者尝试调用 PUT /api/characters/{id}/
- **THEN** 系统返回 HTTP 403

---

### Requirement: 角色删除
系统 SHALL 允许角色所有者删除角色。

#### Scenario: 删除确认
- **WHEN** 角色所有者点击删除并在确认弹窗中确认
- **THEN** 系统删除角色记录，返回 HTTP 204，跳转回角色列表页

#### Scenario: 取消删除
- **WHEN** 用户在确认弹窗中取消
- **THEN** 系统不执行任何操作，关闭弹窗

---

### Requirement: 游戏数据查询
系统 SHALL 提供种族、职业、法术等游戏数据的查询接口，供前端向导和角色卡使用。

#### Scenario: 按规则集查询种族列表
- **WHEN** 前端请求 GET /api/gamedata/races/?ruleset=<id>
- **THEN** 系统返回该规则集下所有种族的列表数据，HTTP 200

#### Scenario: 查询职业详情
- **WHEN** 前端请求 GET /api/gamedata/classes/<slug>/
- **THEN** 系统返回职业完整数据，含各等级特性列表，HTTP 200

#### Scenario: 法术多条件过滤
- **WHEN** 前端请求 GET /api/gamedata/spells/?ruleset=<id>&level=1&char_class=wizard
- **THEN** 系统返回符合所有过滤条件的法术列表，HTTP 200
