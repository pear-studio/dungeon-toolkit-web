## ADDED Requirements

### Requirement: 配置初始等级
职业步骤 SHALL 提供等级输入，允许玩家为每个职业设定 1–20 级，所有职业等级之和不得超过 20。

#### Scenario: 单职业等级设定
- **WHEN** 玩家选择「圣武士」并将等级设为 5
- **THEN** wizardStore 记录 `classes: [{ class_slug: "paladin", level: 5 }]`，总等级 = 5

#### Scenario: 超出总等级上限
- **WHEN** 当前总等级已为 20，玩家尝试再添加一个兼职职业
- **THEN** 系统禁止添加并展示「总等级不能超过 20」提示

### Requirement: 添加兼职职业
玩家 SHALL 能够在主职业之外添加最多 2 个兼职职业（总职业数 ≤ 3，总等级 ≤ 20）。

#### Scenario: 添加兼职
- **WHEN** 玩家已有「圣武士 5 级」，点击「添加兼职」并选择「法师」设为 3 级
- **THEN** wizardStore 更新为 `classes: [{ class_slug: "paladin", level: 5 }, { class_slug: "wizard", level: 3 }]`，总等级 = 8

#### Scenario: 删除兼职
- **WHEN** 玩家点击兼职职业右侧的删除按钮
- **THEN** 该兼职条目从 classes 数组中移除

### Requirement: 计算 ASI 与专长节点
系统 SHALL 根据每个职业的等级计算属性值提升（ASI）触发节点，并在职业特性列表中以醒目标注展示。

#### Scenario: 单职业 ASI 展示
- **WHEN** 玩家选择「战士 6 级」
- **THEN** 特性列表中第 4 级和第 6 级条目标注「⭐ 属性值提升」

#### Scenario: 多职业 ASI 合计
- **WHEN** 玩家配置「战士 4 级 + 游荡者 4 级」
- **THEN** 战士第 4 级和游荡者第 4 级各触发 1 次 ASI，共计 2 次 ASI，汇总展示在职业步骤底部

### Requirement: 多职业前提属性提示
当玩家添加的兼职职业有前提属性要求时，系统 SHALL 展示警告提示，但不强制阻止。

#### Scenario: 前提属性不满足时的警告
- **WHEN** 玩家尝试兼职「战士」，但当前力量属性 < 13
- **THEN** 在兼职条目旁展示「⚠ 需要力量 ≥ 13」，允许继续操作
