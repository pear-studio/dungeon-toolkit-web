## MODIFIED Requirements

### Requirement: 亚种族强制选择
当玩家选择有亚种族的种族时，亚种族选择 MUST 为必填项；未选亚种族时，向导提交按钮 SHALL 保持禁用。

#### Scenario: 有亚种族的种族强制选择
- **WHEN** 玩家选择「精灵」种族（has_subraces = true）
- **THEN** 亚种族选择区域展示「高等精灵」「木精灵」「黑暗精灵」，标注「必选」，未选中时提交不可用

#### Scenario: 无亚种族的种族跳过
- **WHEN** 玩家选择「人类」种族（has_subraces = false）
- **THEN** 不展示亚种族选择区域，直接进行后续步骤

### Requirement: 亚种族属性加成传播
亚种族的属性加成 SHALL 合并进入种族属性加成，并传递给属性总览步骤。

#### Scenario: 亚种族加成叠加基础种族加成
- **WHEN** 玩家选择「精灵（高等精灵）」
- **THEN** wizardStore 中 `race_ability_bonuses` 包含精灵基础加成（敏捷 +2）加上高等精灵加成（智力 +1），合并为 `{ dexterity: 2, intelligence: 1 }`

#### Scenario: 亚种族额外熟练项
- **WHEN** 选择的亚种族提供额外技能或武器熟练（如高等精灵获得一种额外语言和精通一种法师戏法）
- **THEN** 在种族详情区域展示这些额外熟练项，并在角色卡预览中体现
