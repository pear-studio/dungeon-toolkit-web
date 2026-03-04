## ADDED Requirements

### Requirement: 文本对比度标准
所有文本与其背景的对比度必须达到 WCAG 2.1 AA 级标准（≥4.5:1）。

#### Scenario: 正文文本对比度
- **WHEN** 正文文本显示在背景上
- **THEN** 对比度至少为 4.5:1

#### Scenario: 大文本对比度
- **WHEN** 大文本（≥18pt 或 ≥14pt bold）显示在背景上
- **THEN** 对比度至少为 3:1

#### Scenario: 次要文本对比度
- **WHEN** 次要说明文字（slate-400）显示在深色背景上
- **THEN** 对比度至少为 4.5:1，使用 slate-300 替代

### Requirement: 深色主题配色规范
深色主题下的颜色使用必须遵循明确的对比度要求。

#### Scenario: 主要文本颜色
- **WHEN** 在 slate-900 背景上显示主要文本
- **THEN** 使用 text-slate-100 或 text-slate-200，对比度≥7:1

#### Scenario: 次要文本颜色
- **WHEN** 在 slate-900 背景上显示次要文本
- **THEN** 使用 text-slate-300，对比度≥5:1

#### Scenario: 占位符文本颜色
- **WHEN** 在 slate-700 背景上显示输入框占位符
- **THEN** 使用 placeholder-slate-400，对比度≥4.5:1

#### Scenario: 强调文本颜色
- **WHEN** 需要强调文本（如选中状态）
- **THEN** 使用 text-amber-400，在 slate-800/900 背景上对比度≥4.5:1

### Requirement: 功能色使用规范
功能色（成功、警告、错误）必须同时使用颜色和图标/文字标识。

#### Scenario: 成功状态
- **WHEN** 显示成功消息
- **THEN** 使用 green-400/green-500 配合成功图标或"成功"文字

#### Scenario: 错误状态
- **WHEN** 显示错误消息
- **THEN** 使用 red-400/red-500 配合错误图标或"错误"文字

#### Scenario: 警告状态
- **WHEN** 显示警告消息
- **THEN** 使用 yellow-400/yellow-500 配合警告图标或"警告"文字

### Requirement: 对比度验证流程
所有新增或修改的 UI 组件必须通过对比度验证。

#### Scenario: 设计阶段验证
- **WHEN** 设计新组件或修改现有组件
- **THEN** 使用对比度检查工具验证所有颜色组合

#### Scenario: 代码审查验证
- **WHEN** 提交代码审查
- **THEN** 审查者必须验证对比度是否符合标准

#### Scenario: 自动化验证
- **WHEN** 运行 Lighthouse 审计
- **THEN** 对比度相关检查必须全部通过
