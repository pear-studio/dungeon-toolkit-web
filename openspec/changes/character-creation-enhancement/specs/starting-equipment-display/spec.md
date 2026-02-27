## ADDED Requirements

### Requirement: 展示背景初始物品包
背景步骤 SHALL 在背景详情区域展示该背景依据玩家手册规定的初始物品清单，展示为只读列表，不需要玩家做选择。

#### Scenario: 展示物品清单
- **WHEN** 玩家选择「侍僧」背景
- **THEN** 在背景详情卡片底部展示初始物品：「圣徽、祈祷书、5 根香、一套祭司服、一套普通衣物、腰包（含 15 金币）」

#### Scenario: 物品有 items.json 关联详情
- **WHEN** 物品清单中包含可在 items.json 中查到的物品 slug
- **THEN** 物品名称旁显示 tooltip 或折叠区域，展示重量/价值等简要属性

#### Scenario: 未选背景时不显示物品区域
- **WHEN** 玩家尚未选择任何背景
- **THEN** 背景详情区域不渲染，物品清单也不显示

### Requirement: items.json 物品信息库
系统 SHALL 维护一份 `backend/data/dnd5e_2014/items.json`，包含玩家手册第五章所有物品条目，字段包括：`slug`、`name`（中文）、`category`（武器/护甲/冒险装备/工具/货币）、`cost`、`weight`、`description`（如有）。

#### Scenario: 物品数据完整性
- **WHEN** 背景初始物品中引用了某物品 slug
- **THEN** 该 slug 在 items.json 中 MUST 存在对应条目

#### Scenario: 物品分类覆盖
- **WHEN** items.json 被导入
- **THEN** 至少包含武器、护甲、冒险装备、工具四大分类的条目
