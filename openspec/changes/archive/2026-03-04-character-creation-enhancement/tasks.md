## 1. 数据层：物品数据库

- [ ] 1.1 调查 `rules_source/DND5e_chm/玩家手册/装备/` 目录结构，确认 HTML 文件列表
- [ ] 1.2 新建 `backend/data/parsers/parse_items.py`，从装备章节 HTML 解析武器/护甲/冒险装备/工具四大分类
- [ ] 1.3 运行 `parse_items.py`，生成 `backend/data/dnd5e_2014/items.json`，验证条目数 ≥ 150
- [ ] 1.4 在 Django 中新增或确认 `Item` 模型（slug, name, category, cost, weight, description）
- [ ] 1.5 在 `import_gamedata.py` 中添加 Item 导入逻辑（`update_or_create`）
- [ ] 1.6 运行导入脚本，验证数据库中 Item 记录正确写入

## 2. 数据层：职业数据补全

- [ ] 2.1 调查 `rules_source/DND5e_chm/玩家手册/职业/` 各职业 HTML 结构
- [ ] 2.2 更新 `parse_classes.py`，提取每个职业的 `features`（按等级）和 `skill_choices`（可选技能列表与数量）
- [ ] 2.3 运行 `parse_classes.py`，更新 `backend/data/dnd5e_2014/classes.json`，验证邪术师描述正确（「与强大存在签订契约，获得奥秘爆发」）
- [ ] 2.4 更新 `parse_classes.py` 以提取所有子职业，修复 Ranger/Sorcerer 「Title Not Found」警告
- [ ] 2.5 更新 Django `CharacterClass` 序列化器以返回 `features` 和 `skill_choices` 字段
- [ ] 2.6 更新 `frontend/src/lib/api.ts` 中 Class 类型，添加 `features` 和 `skill_choices` 字段

## 3. 数据层：背景数据补全

- [ ] 3.1 更新 `parse_backgrounds.py`，提取每个背景的 `feature_name`、`feature_description`、`starting_equipment`（物品文本列表）
- [ ] 3.2 运行 `parse_backgrounds.py`，更新 `backend/data/dnd5e_2014/backgrounds.json`，抽查「侍僧」特性「庇护所」
- [ ] 3.3 更新 `import_gamedata.py`，将 `starting_equipment` 写入 Background 模型（JSON 字段或文本字段）
- [ ] 3.4 更新 DRF 序列化器，Background API 返回 `feature_description` 和 `starting_equipment` 字段
- [ ] 3.5 更新 `frontend/src/lib/api.ts` 中 Background 类型，添加 `feature_description` 和 `starting_equipment` 字段

## 4. 前端：wizardStore 重构

- [ ] 4.1 在 `wizardStore.ts` 中将 `class_slug` 字段替换为 `classes: Array<{ class_slug: string; level: number }>`
- [ ] 4.2 添加 `chosen_skills: string[]` 字段用于存储职业步骤的技能熟练选择
- [ ] 4.3 添加 `_v: 2` 版本字段，实现旧版本（`_v: 1` 或无版本）数据自动迁移函数
- [ ] 4.4 实现 `allSkillProficiencies` selector：`chosen_skills ∪ 背景固定技能`，去重返回
- [ ] 4.5 实现 `totalLevel` selector：所有 classes 的 level 之和

## 5. 前端：职业步骤重构（ClassSection）

- [ ] 5.1 将职业选择 UI 改为支持多职业条目，每个条目包含职业选择 + 等级输入
- [ ] 5.2 添加「添加兼职」按钮，限制总职业数 ≤ 3、总等级 ≤ 20
- [ ] 5.3 实现技能熟练选择 UI：展示该职业可选技能列表，支持多选（限制数量），已有背景技能标注禁用
- [ ] 5.4 实现职业特性列表展示区域（基于当前等级过滤），ASI 节点醒目标注「⭐ 属性值提升」
- [ ] 5.5 多职业时展示兼职前提属性警告（非阻断）

## 6. 前端：种族步骤修复（RaceSection）

- [ ] 6.1 有亚种族的种族，亚种族选择区域添加「必选」标注
- [ ] 6.2 将亚种族属性加成合并到 wizardStore 的 `race_ability_bonuses` 字段（基础种族 + 亚种族）
- [ ] 6.3 展示亚种族提供的额外熟练项

## 7. 前端：属性步骤重构（AbilitySection）

- [ ] 7.1 属性步骤中去掉独立的「属性总览」子步骤/标签，改为两个纵向面板（分配方式 + 只读总览）在同一视图
- [ ] 7.2 总览面板实时读取 `abilities` + `race_ability_bonuses`，展示最终属性值和调整值

## 8. 前端：背景步骤优化（DescribeSection）

- [ ] 8.1 背景卡片副标题移除 `.slice(0, 2)` 截断和省略号，完整展示所有技能
- [ ] 8.2 背景详情区域：特性字段改为读取 `feature_description`，若为空或占位符则不渲染
- [ ] 8.3 背景详情区域底部添加初始物品展示列表（读取 `starting_equipment` 字段）
- [ ] 8.4 验证所有技能名通过 `skillZh()` 转换，不出现英文 slug

## 9. 前端：角色名去重

- [ ] 9.1 排查所有步骤，确认角色名输入框只存在于 `DescribeSection`
- [ ] 9.2 删除其他位置的角色名输入（如 `ClassSection` 或 `CreatePage` 顶部如有）

## 10. 前端：角色卡预览（CharacterPreview 新组件）

- [ ] 10.1 新建 `frontend/src/components/wizard/CharacterPreview.tsx`
- [ ] 10.2 实现基本信息区（角色名、种族+亚种族、职业+等级、阵营、年龄、性别）
- [ ] 10.3 实现属性值区（六项属性最终值 + 调整值）
- [ ] 10.4 实现战斗数据区（熟练加值、HP 估算）
- [ ] 10.5 实现技能熟练区（读取 `allSkillProficiencies` selector，显示中文名）
- [ ] 10.6 实现背景与物品区（背景名+特性+初始装备列表）
- [ ] 10.7 实现职业特性摘要区（所有职业当前等级内获得的特性名列表）
- [ ] 10.8 处理数据不完整情况：各区域缺失数据显示「—」，顶部展示未完成提示
- [ ] 10.9 将 `CharacterPreview` 作为向导最后一步集成到 `CreatePage`

## 11. 收尾验证

- [ ] 11.1 端到端测试：从种族到预览完整走通一个「精灵（高等精灵）法师 3 级 + 圣武士 2 级」角色
- [ ] 11.2 确认所有技能/属性名在 UI 中均以中文展示，无英文 slug 裸露
- [ ] 11.3 确认 `wizardStore` 旧版本数据迁移正常（清 localStorage 后恢复）
- [ ] 11.4 确认背景特性文本为真实内容，无「背景特性」占位符
- [ ] 11.5 确认职业特性数据所有职业非空（抽查战士、法师、邪术师）
