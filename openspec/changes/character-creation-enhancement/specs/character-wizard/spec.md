## MODIFIED Requirements

### Requirement: wizardStore 状态结构
wizardStore MUST 支持多职业、初始等级、技能熟练选择、装备字段，并向后兼容旧版本数据。

状态结构更新为：
```ts
{
  _v: 2,                              // 版本字段，用于迁移检测
  name: string,                       // 角色名（仅在描述步骤）
  race_slug: string,
  race_custom_name: string,
  subrace_slug: string,
  gender: string,
  age: string,
  classes: Array<{                    // 替代原 class_slug（单字段）
    class_slug: string
    level: number
  }>,
  chosen_skills: string[],            // 职业步骤选择的技能 slug 列表
  ability_method: string,
  abilities: Record<string, number>,
  background_slug: string,
  alignment: string,
  appearance: string,
  personality_traits: string,
  ideals: string,
  bonds: string,
  flaws: string,
}
```

#### Scenario: 旧版本数据自动迁移
- **WHEN** localStorage 中存在 `_v: 1` 或无版本字段的旧状态（含 `class_slug` 字符串字段）
- **THEN** 系统自动将其迁移为 `classes: [{ class_slug: oldValue, level: 1 }]`，并设置 `_v: 2`

#### Scenario: 角色名唯一入口
- **WHEN** 玩家在描述步骤之外的任何步骤
- **THEN** 不存在角色名输入框；角色名仅在描述步骤的 `DescribeSection` 中填写

#### Scenario: 技能熟练汇总 selector
- **WHEN** 调用 `useWizardStore` 的 `allSkillProficiencies` selector
- **THEN** 返回 `chosen_skills ∪ 背景固定技能`，去重后的 slug 数组
