## 1. 准备工作

- [x] 1.1 安装 lucide-react 图标库：`npm install lucide-react`
- [x] 1.2 修改 index.html 的 lang 属性从 `en` 改为 `zh-CN`
- [x] 1.3 在 index.css 中添加统一的焦点样式规范

## 2. 核心组件修复

- [x] 2.1 修改 DashboardPage.tsx：将可点击卡片改为 button 元素，添加焦点样式
- [x] 2.2 修改 RobotPlazaPage.tsx：将 RobotCard 改为 button 元素，添加焦点样式
- [x] 2.3 修改 RobotDetailPage.tsx：添加焦点样式，优化键盘导航
- [x] 2.4 修改 MyRobotsPage.tsx：将可点击元素改为 button，添加焦点样式
- [x] 2.5 修改 RobotFormPage.tsx：添加焦点样式
- [x] 2.6 修改 LoginPage.tsx：添加焦点样式
- [x] 2.7 修改 RegisterPage.tsx：添加焦点样式
- [x] 2.8 修改 ProtectedRoute.tsx：优化加载状态的无障碍支持

## 3. Emoji 替换为图标

- [x] 3.1 在 DashboardPage.tsx 中用 lucide 图标替换所有 emoji
- [x] 3.2 在 RobotPlazaPage.tsx 中用 lucide 图标替换 emoji
- [x] 3.3 在 RobotDetailPage.tsx 中用 lucide 图标替换 emoji
- [x] 3.4 在 MyRobotsPage.tsx 中用 lucide 图标替换 emoji
- [x] 3.5 在 LoginPage.tsx 中用 lucide 图标替换 emoji
- [x] 3.6 在 RegisterPage.tsx 中用 lucide 图标替换 emoji
- [x] 3.7 在 ProtectedRoute.tsx 中用 lucide 图标替换 emoji
- [x] 3.8 为所有装饰性图标添加 aria-hidden="true"

## 4. 对比度修复

- [x] 4.1 将所有页面的 text-slate-400 改为 text-slate-300（正文文本）
- [x] 4.2 验证所有颜色组合的对比度达到 WCAG AA 标准
- [ ] 4.3 更新 DESIGN_SYSTEM.md 添加对比度数据表

## 5. 屏幕阅读器支持

- [x] 5.1 为动态内容（错误提示、加载状态）添加 aria-live 属性（role="alert"）
- [x] 5.2 验证所有表单控件的 label 关联
- [x] 5.3 为功能图标添加适当的 aria-label

## 6. 测试与验证

- [ ] 6.1 使用 Tab 键测试所有页面的键盘导航
- [ ] 6.2 验证所有交互元素的焦点环可见性
- [ ] 6.3 使用浏览器插件验证颜色对比度
- [ ] 6.4 运行 Lighthouse 审计并记录分数
- [ ] 6.5 在屏幕阅读器中测试关键页面（可选）

## 7. 文档更新

- [ ] 7.1 更新 DESIGN_SYSTEM.md 添加无障碍规范章节
- [ ] 7.2 添加图标使用规范文档
- [ ] 7.3 记录对比度验证工具和流程
