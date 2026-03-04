## ADDED Requirements

### Requirement: SVG 图标库使用
系统必须使用 lucide-react 图标库替代 emoji 作为功能图标。

#### Scenario: 安装图标库
- **WHEN** 项目需要图标
- **THEN** 从 lucide-react 导入，不使用外部字体或图片

#### Scenario: 图标尺寸统一
- **WHEN** 使用图标
- **THEN** 统一使用 24x24 默认尺寸，或按比例缩放

#### Scenario: 图标线条粗细
- **WHEN** 使用图标
- **THEN** 使用默认 2px 线条粗细，保持视觉一致性

### Requirement: Emoji 使用限制
禁止在功能性 UI 元素中使用 emoji，仅允许在非功能性文本中使用。

#### Scenario: 功能图标替换
- **WHEN** 需要表示功能（如搜索、设置、用户）
- **THEN** 使用 SVG 图标，不使用 emoji

#### Scenario: 状态指示替换
- **WHEN** 需要表示状态（如在线、离线）
- **THEN** 使用 SVG 图标或色块配合文字，不使用 emoji

#### Scenario: 装饰性 emoji 处理
- **WHEN** 页面包含装饰性 emoji
- **THEN** 添加 `aria-hidden="true"` 属性

### Requirement: 图标可访问性处理
所有图标必须正确处理以确保屏幕阅读器用户可以理解。

#### Scenario: 纯装饰图标
- **WHEN** 图标仅用于装饰
- **THEN** 添加 `aria-hidden="true"`，不占用 tab 顺序

#### Scenario: 按钮内图标
- **WHEN** 图标在按钮内且按钮有文字
- **THEN** 图标添加 `aria-hidden="true"`，文字提供描述

#### Scenario: 独立图标按钮
- **WHEN** 按钮仅包含图标无文字
- **THEN** 图标添加 `aria-label` 提供功能描述

### Requirement: 图标颜色规范
图标颜色必须遵循设计系统规范，确保对比度和一致性。

#### Scenario: 主要图标颜色
- **WHEN** 使用主要功能图标
- **THEN** 使用 text-slate-200 或 text-white

#### Scenario: 强调图标颜色
- **WHEN** 使用强调或选中状态图标
- **THEN** 使用 text-amber-400

#### Scenario: 状态图标颜色
- **WHEN** 使用状态图标（成功、警告、错误）
- **THEN** 使用对应的功能色（green-400、yellow-400、red-400）

### Requirement: 图标加载性能
图标加载不得影响页面性能或导致布局偏移。

#### Scenario: 按需导入
- **WHEN** 使用图标
- **THEN** 仅导入使用的图标，不使用通配符导入

#### Scenario: 无布局偏移
- **WHEN** 图标加载
- **THEN** 不导致页面布局变化或内容跳动

#### Scenario: Tree-shaking 支持
- **WHEN** 构建生产版本
- **THEN** 未使用的图标被自动移除，减小打包体积
