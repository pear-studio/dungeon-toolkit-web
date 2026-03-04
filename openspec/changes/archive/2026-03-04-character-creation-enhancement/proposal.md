## Why

角色创建向导当前存在多处功能缺失与数据错误：职业描述不完整（如邪术师契约来源缺失）、亚种族选择不完整、属性分配方法与最终总览脱节、背景/职业技能熟练选择缺失、背景特性显示无意义占位文本、缺少初始物品选择、角色名在两处重复出现、不支持多职业与初始等级设定、最终无角色卡预览。需要一次系统性补全，使向导产出一个规则完整、数据可信的 D&D 5e 2014 角色。

## What Changes

- **职业数据补全**：所有 12 个职业需从玩家手册提取完整的职业描述（包括邪术师「与强大存在签订契约，获得奥秘爆发」等）、职业特性列表（按等级），并关联正确的子职业选项；不单独修正某一职业，统一从规则来源重新解析
- **亚种族选择**：种族步骤中选择有亚种族的种族时，必须选择亚种族；亚种族影响属性加成与技能/武器熟练项
- **属性步骤重构**：三种方式（标准值/点数购买/随机骰）只决定初始六项数值，属性总览与分配方法统一在同一步骤展示
- **技能熟练选择**：选择职业时，按职业规则展示可选技能列表供玩家选择；选择背景时同理（背景技能已固定，无需选择，仅展示）
- **背景展示优化**：背景卡片副标题直接显示全部技能名称，不截断省略；特性字段从数据库读取真实文本，不显示占位符
- **初始物品选择**：背景步骤中展示该背景在玩家手册中规定的初始物品包（固定给予，无需选择）；同步整理全书装备数据（武器、护甲、冒险装备、工具等），建立 `items.json` 作为物品信息库
- **角色名去重**：角色名仅在"描述"步骤填写，移除重复出现的其他位置
- **多职业 & 初始等级**：支持设定角色初始等级（1–20），支持多职业（兼职），自动计算各职业获得的职业特性、属性值提升次数和专长
- **角色卡预览**：最后一步展示完整角色卡，包含：种族/职业/等级、属性值与调整值、熟练加值、技能熟练列表、背景特性、初始装备、HP 估算

## Capabilities

### New Capabilities

- `class-features-display`：按等级展示职业特性，支持多职业合并显示
- `multiclass-level-config`：配置初始等级与多职业，计算 ASI/专长触发节点
- `skill-proficiency-selection`：职业步骤中的技能熟练项选择 UI
- `starting-equipment-display`：展示背景提供的初始物品包（从 `backgrounds.json` 读取），关联 `items.json` 显示物品详情
- `items-database`：从玩家手册第五章整理武器、护甲、冒险装备、工具完整数据，写入 `backend/data/dnd5e_2014/items.json`
- `character-sheet-preview`：基于所有向导状态生成只读角色卡预览

### Modified Capabilities

- `character-wizard`：向导步骤顺序与状态结构调整（增加等级/多职业/装备字段），角色名字段去重
- `race-subrace-selection`：亚种族选择变为强制项（有亚种族时），并向 wizardStore 传递亚种族属性加成
- `background-display`：背景卡片技能展示不截断；特性字段改为读取真实数据

## Impact

- **前端**：`RaceSection.tsx`、`ClassSection.tsx`、`DescribeSection.tsx`、`AbilitySection.tsx`、新增 `EquipmentSection.tsx`、`CharacterPreview.tsx`、`wizardStore.ts`（状态字段扩展）
- **后端数据**：`classes.json` / `subclasses.json` 需补全职业特性列表；`backgrounds.json` 需补全特性文本与初始物品包字段；新增 `items.json`；`import_gamedata.py` 同步更新
- **Django 模型**：`ClassFeature` 模型确认存在；新增 `Item` 模型（或扩展现有模型）存储物品数据
- **解析脚本**：新增 `parse_items.py` 从 `rules_source/DND5e_chm/玩家手册/装备/` 提取物品数据
- **规范遵守**：所有数据从 `rules_source/DND5e_chm/玩家手册` 读取，技能 slug 经 `skillZh()` 转换后方可渲染（见 `docs/conventions/data-sources.md`）
