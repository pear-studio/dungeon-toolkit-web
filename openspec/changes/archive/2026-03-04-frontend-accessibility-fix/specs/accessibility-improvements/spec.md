## ADDED Requirements

### Requirement: 键盘导航支持
系统必须支持完整的键盘导航功能，确保键盘用户可以访问所有交互元素。

#### Scenario: Tab 键顺序访问
- **WHEN** 用户按下 Tab 键
- **THEN** 焦点按逻辑顺序移动到下一个可交互元素（链接、按钮、输入框）

#### Scenario: Enter 键激活按钮
- **WHEN** 焦点在按钮上且用户按下 Enter 键
- **THEN** 按钮被激活，触发点击事件

#### Scenario: Space 键激活按钮
- **WHEN** 焦点在按钮上且用户按下 Space 键
- **THEN** 按钮被激活，触发点击事件

#### Scenario: 焦点不陷入死循环
- **WHEN** 用户连续按 Tab 键遍历所有元素后
- **THEN** 焦点回到页面顶部，而不是困在某个元素中

### Requirement: 语义化按钮元素
所有可交互的卡片必须使用 `<button>` 元素而非 `<div onClick>`。

#### Scenario: 卡片可被 Tab 键访问
- **WHEN** 用户使用 Tab 键导航
- **THEN** 所有可点击卡片都能获得焦点

#### Scenario: 卡片支持 Enter 键激活
- **WHEN** 焦点在卡片上且用户按下 Enter 键
- **THEN** 卡片被点击，触发导航或操作

#### Scenario: 卡片支持 Space 键激活
- **WHEN** 焦点在卡片上且用户按下 Space 键
- **THEN** 卡片被点击，触发导航或操作

### Requirement: 焦点可见性
所有交互元素在获得焦点时必须显示清晰可见的焦点环。

#### Scenario: 按钮焦点环
- **WHEN** 按钮获得焦点
- **THEN** 显示 2px 宽的 amber-500 实线环，带 2px 偏移

#### Scenario: 输入框焦点环
- **WHEN** 输入框获得焦点
- **THEN** 显示 2px 宽的 amber-500 实线环

#### Scenario: 卡片焦点环
- **WHEN** 卡片按钮获得焦点
- **THEN** 显示 2px 宽的 amber-500 实线环，带 2px 偏移

#### Scenario: 链接焦点环
- **WHEN** 链接获得焦点
- **THEN** 显示 2px 宽的 amber-500 实线环

### Requirement: 屏幕阅读器支持
系统必须为屏幕阅读器用户提供适当的 ARIA 属性。

#### Scenario: 装饰性元素隐藏
- **WHEN** 页面包含装饰性 emoji 或图标
- **THEN** 添加 `aria-hidden="true"` 属性，屏幕阅读器跳过朗读

#### Scenario: 动态内容通知
- **WHEN** 错误提示、成功消息等动态内容出现
- **THEN** 使用 `aria-live="polite"` 或 `role="alert"`，屏幕阅读器自动朗读

#### Scenario: 表单标签关联
- **WHEN** 表单控件存在
- **THEN** 使用 `<label>` 元素并通过 `htmlFor` 属性与输入框关联

#### Scenario: 页面语言声明
- **WHEN** 页面加载
- **THEN** `<html>` 标签设置 `lang="zh-CN"`，屏幕阅读器使用中文朗读

### Requirement: 图标可访问性
所有图标必须正确处理以确保屏幕阅读器用户理解其含义。

#### Scenario: 纯装饰图标
- **WHEN** 图标仅用于装饰，不传达信息
- **THEN** 添加 `aria-hidden="true"`，屏幕阅读器跳过

#### Scenario: 功能性图标
- **WHEN** 图标传达功能信息（如搜索、菜单）
- **THEN** 添加 `aria-label` 提供文字描述，或配合可见文字使用

#### Scenario: 状态图标
- **WHEN** 图标表示状态（如在线、离线）
- **THEN** 配合文字标签使用，不单独依赖颜色或形状传达信息
