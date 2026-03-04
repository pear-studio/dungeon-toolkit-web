## Why

前端项目当前存在严重的无障碍访问问题，导致键盘用户和屏幕阅读器用户无法正常使用网站。同时文本对比度未达到 WCAG 2.1 AA 标准，影响视觉障碍用户的可读性。此变更旨在修复 P0+P1 级别的关键问题，确保网站对所有用户都可访问。

## What Changes

- **修复键盘可达性**：将所有可点击的 `<div onClick>` 卡片改为 `<button>` 元素
- **增强焦点可见性**：为所有交互元素添加可见的焦点环样式
- **提升对比度**：将文本对比度从 3.8:1 提升至 WCAG AA 标准 4.5:1 以上
- **改进屏幕阅读器支持**：为装饰性 emoji 添加 `aria-hidden`，为动态内容添加 `aria-live`
- **替换 emoji 为 SVG 图标**：使用专业图标库提升 UI 品质
- **完善语言属性**：将 HTML 语言从 `en` 改为 `zh-CN`
- **添加焦点管理模板**：为所有组件建立统一的焦点样式规范

## Capabilities

### New Capabilities
- `accessibility-improvements`: 无障碍访问改进，包括键盘导航、焦点管理、屏幕阅读器支持
- `color-contrast-fix`: 颜色对比度修复，确保所有文本符合 WCAG AA 标准
- `icon-system-upgrade`: 图标系统升级，从 emoji 迁移到 SVG 图标

### Modified Capabilities
- 无

## Impact

- **前端组件**：所有页面组件需要修改（DashboardPage、RobotPlazaPage、LoginPage、RegisterPage 等）
- **样式系统**：需要更新 index.css 和 DESIGN_SYSTEM.md
- **HTML 结构**：index.html 需要修改 lang 属性
- **依赖**：需要安装 SVG 图标库（lucide-react）
- **用户影响**：无破坏性变更，仅改进现有功能
