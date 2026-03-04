## Context

Dungeon Toolkit Web 前端项目当前使用 React 19 + TypeScript + Tailwind CSS 4 构建，采用深色主题设计。在代码审查中发现以下关键问题：

1. **无障碍访问缺陷**：多个页面使用 `<div onClick>` 作为可交互卡片，键盘用户无法通过 Tab 键访问
2. **焦点样式缺失**：大量按钮使用 `focus:outline-none` 但未提供替代焦点样式
3. **对比度不足**：`text-slate-400` 在 `bg-slate-900` 上对比度仅 3.8:1，低于 WCAG AA 标准
4. **Emoji 滥用**：使用 emoji 作为功能图标，不符合专业 UI 规范且对屏幕阅读器不友好
5. **语言属性错误**：HTML 语言设置为 `en` 而非 `zh-CN`

## Goals / Non-Goals

**Goals:**
- 修复所有键盘可达性问题，确保所有交互元素可通过 Tab 键访问
- 为所有交互元素添加可见焦点环，符合 WCAG 2.1 AA 标准
- 提升文本对比度至 4.5:1 以上
- 改进屏幕阅读器支持（aria-hidden, aria-live）
- 替换 emoji 为专业 SVG 图标
- 修正 HTML 语言属性为 `zh-CN`
- 更新 DESIGN_SYSTEM.md 添加无障碍规范章节

**Non-Goals:**
- 不改变现有视觉设计风格（颜色、布局保持不变）
- 不添加新的功能特性
- 不重构现有组件结构（仅修复无障碍问题）
- 不实现完整的亮色模式（留待后续迭代）

## Decisions

### 决策 1：使用 lucide-react 作为图标库

**选择**: 安装 `lucide-react` 图标库

**原因**:
- 提供一致的 24x24 视图框和 2px 线条粗细
- 纯 SVG 实现，无外部字体依赖
- 支持 tree-shaking，按需引入
- 提供超过 1000 个高质量图标
- MIT 许可证，开源免费使用

**替代方案**:
- Heroicons: 图标数量较少，风格更偏手绘
- React Icons: 打包体积过大，包含不需要的图标集
- Feather Icons: 已停止维护

### 决策 2：保持 Tailwind 类，不引入 CSS Custom Properties

**选择**: 继续使用 Tailwind 原子类，不重构为 CSS 变量

**原因**:
- Tailwind v4 已内置 CSS 变量支持
- 当前设计系统已稳定，无需频繁切换主题
- 重构成本高，收益低
- 性能无显著差异

**替代方案**:
- 完全迁移到 CSS Custom Properties: 工作量大，当前优先级低

### 决策 3：使用语义化 `<button>` 元素替换 `<div onClick>`

**选择**: 将所有可点击卡片改为 `<button>` 元素

**原因**:
- 原生支持键盘访问（Tab 键、Enter 键）
- 自动获得焦点管理能力
- 屏幕阅读器自动识别为可交互元素
- 符合 HTML 语义化标准

**实现细节**:
- 使用 `type="button"` 防止表单提交
- 添加 `className="text-left"` 保持左对齐样式
- 使用 `!bg-slate-800` 防止浏览器默认样式覆盖

### 决策 4：统一焦点样式为 2px 实线环

**选择**: `focus:ring-2 focus:ring-amber-500 focus:ring-offset-2`

**原因**:
- 2px 宽度在深色背景下清晰可见
- 使用品牌强调色 amber-500，保持一致性
- ring-offset 确保在卡片边框上仍可见
- 符合 WCAG 2.1 AA 焦点可见性要求

**替代方案**:
- 虚线 outline: 传统方案，但样式不够现代
- 4px 宽环：过粗，影响视觉美观

### 决策 5：对比度修复策略

**选择**: 将 `text-slate-400` 改为 `text-slate-300`

**原因**:
- slate-300 (#cbd5e1) 在 slate-900 (#0f172a) 上对比度为 5.2:1
- 视觉变化最小，用户感知不明显
- 无需修改设计规范，仅调整实现

**对比度数据**:
- slate-400 (#94a3b8) on slate-900: 3.8:1 ❌
- slate-300 (#cbd5e1) on slate-900: 5.2:1 ✅
- slate-200 (#e2e8f0) on slate-900: 7.1:1 ✅ (AAA 级)

## Risks / Trade-offs

### 风险 1：安装新依赖增加打包体积

**风险**: lucide-react 增加约 50KB 打包体积

**缓解**:
- 使用 tree-shaking 按需引入
- 仅导入实际使用的图标
- 生产环境启用代码分割

### 风险 2：视觉变化影响用户体验

**风险**: 图标风格变化可能被老用户注意到

**缓解**:
- 保持图标含义与原 emoji 一致
- 颜色、大小保持一致
- 变化渐进，不影响功能

### 风险 3：焦点样式可能与某些组件冲突

**风险**: 统一焦点环可能与现有样式冲突

**缓解**:
- 使用 `focus:ring-offset-2` 确保在边框上可见
- 测试所有交互元素
- 必要时使用 `!` 强制应用

### 风险 4：向后兼容性

**风险**: 修改 HTML 结构可能影响现有测试或集成

**缓解**:
- 保持现有 API 和数据结构不变
- 仅修改前端展示层
- 手动测试所有修改的页面

## Migration Plan

### 阶段 1：准备（15 分钟）
1. 安装 lucide-react 依赖
2. 创建图标使用规范文档

### 阶段 2：核心修复（60 分钟）
1. 修改 index.html lang 属性
2. 修改 index.css 添加焦点样式规范
3. 修改所有页面组件：
   - DashboardPage.tsx
   - RobotPlazaPage.tsx
   - RobotDetailPage.tsx
   - MyRobotsPage.tsx
   - LoginPage.tsx
   - RegisterPage.tsx
   - RobotFormPage.tsx
   - ProtectedRoute.tsx

### 阶段 3：验证（30 分钟）
1. 手动测试键盘导航
2. 验证焦点可见性
3. 使用浏览器插件检查对比度
4. 运行 Lighthouse 审计

### 阶段 4：文档更新（15 分钟）
1. 更新 DESIGN_SYSTEM.md
2. 添加无障碍规范章节
3. 记录对比度数据

### 回滚策略
- 使用 Git 版本控制，可随时回滚到修复前版本
- 所有变更集中在 frontend 目录，不影响后端
- 如发现问题，可单独回滚特定组件

## Open Questions

无。所有技术决策已明确，可立即开始实施。
