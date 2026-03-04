# 前端代码质量检查机制

## 📋 目的

确保前端代码符合无障碍规范，防止 emoji 使用、低对比度文本等问题再次出现。

---

## 🔧 检查工具

### 统一检查脚本（推荐）

在项目根目录执行：

```powershell
# 运行完整检查（emoji、对比度、焦点样式、ARIA 属性）
powershell -ExecutionPolicy Bypass -File scripts/check-frontend-quality.ps1
```

**检查内容**：
1. ✅ 检测所有 emoji 字符（Unicode 范围 U+1F300-U+1F9FF）
2. ✅ 检测低对比度文本（text-slate-500/600/700）
3. ✅ 检测缺少焦点样式的按钮
4. ✅ 检测缺少 aria 属性的图标

**输出示例**：
```
================================
  Frontend Code Quality Check
================================

Check 1/4: Detecting emoji characters...
PASS: No emoji found

Check 2/4: Detecting low contrast text...
WARN: Found low contrast text (first 20):
  MyRobotsPage.tsx:180
  RobotPlazaPage.tsx:142

Check 3/4: Detecting buttons without focus styles...
PASS: All buttons have focus styles

Check 4/4: Detecting icons without aria attributes...
PASS: All icons have aria attributes

================================
  Check Complete!
  Duration: 136ms
  Errors: 0
  Warnings: 1
================================

PASSED with warnings (optimization recommended)
```

**退出码**：
- `0`: 检查通过（可能有警告）
- `1`: 检查失败（发现错误，如 emoji）

**注意事项**：
- 检查 2 会报告使用 `text-slate-500/600/700` 的地方，这些是警告，不是错误
- 如果希望完全无警告，可以将所有 `text-slate-400` 改为 `text-slate-300`
- 某些装饰性文本使用 `text-slate-500` 是可以接受的（如空状态图标）

---

## ✅ 检查清单

### 提交前必检项目

#### 1. Emoji 检查
- [ ] 代码中无 emoji 字符（🏰🤖⚙️🔍🎯等）
- [ ] 所有图标使用 lucide-react 库
- [ ] 装饰性图标添加 `aria-hidden="true"`

#### 2. 颜色对比度
- [ ] 正文文本不使用 `text-slate-500` 或更低
- [ ] 次要文本最低使用 `text-slate-400`
- [ ] 推荐正文使用 `text-slate-300`

#### 3. 焦点样式
- [ ] 所有 `<button>` 元素有 `focus:` 相关样式
- [ ] 所有 `<input>` 元素有 `focus:` 相关样式
- [ ] 所有可交互元素有 `focus:outline-none` 和 `focus:ring-*`

#### 4. 语义化 HTML
- [ ] 可点击元素使用 `<button>` 而非 `<div onClick>`
- [ ] 所有表单控件有 `<label>` 关联
- [ ] 动态内容区域有 `role="alert"` 或其他 ARIA 角色

---

## 🚀 自动化检查流程

### Git Pre-commit Hook（推荐）

创建 `.git/hooks/pre-commit` 文件：

```bash
#!/bin/bash

echo "Running frontend quality checks..."

# 使用 PowerShell 脚本检查（如果在 Windows 环境）
if command -v powershell &> /dev/null; then
    powershell -ExecutionPolicy Bypass -File scripts/check-frontend-quality.ps1
    if [ $? -ne 0 ]; then
        echo "❌ Frontend quality check failed."
        exit 1
    fi
else
    # 简单检查（如果没有 PowerShell）
    if grep -r --include="*.tsx" --include="*.ts" -l $'[\xF0-\xF7][\x80-\xBF][\x80-\xBF][\x80-\xBF]' frontend/src/ 2>/dev/null; then
        echo "❌ Found emoji in code. Please use lucide-react icons instead."
        exit 1
    fi
fi

echo "✅ Quality checks passed!"
exit 0
```

使其可执行：
```bash
chmod +x .git/hooks/pre-commit
```

### CI/CD 集成

在 GitHub Actions 或其他 CI 工具中添加：

```yaml
- name: Frontend Quality Check
  shell: pwsh
  run: |
    powershell -ExecutionPolicy Bypass -File scripts/check-frontend-quality.ps1
```

---

## 📖 规范文档

### 图标使用规范

**❌ 错误示例**：
```tsx
<div>🏰</div>
<div>🤖</div>
<div>⚙️</div>
```

**✅ 正确示例**：
```tsx
import { Castle, Bot, Settings } from 'lucide-react'

<Castle className="w-12 h-12 text-amber-400" aria-hidden="true" />
<Bot className="w-8 h-8 text-slate-300" aria-hidden="true" />
<Settings className="w-8 h-8" aria-label="设置" />
```

### 颜色对比度规范

**❌ 错误示例**：
```tsx
<p className="text-slate-500">正文文本</p>
<p className="text-slate-600">说明文字</p>
```

**✅ 正确示例**：
```tsx
<p className="text-slate-300">正文文本（对比度 7.5:1，AAA 级）</p>
<p className="text-slate-400">次要文本（对比度 4.5:1，AA 级）</p>
```

### 焦点样式规范

**❌ 错误示例**：
```tsx
<button onClick={handler}>点击</button>
<input type="text" />
```

**✅ 正确示例**：
```tsx
<button 
  onClick={handler}
  className="focus:outline-none focus:ring-2 focus:ring-amber-500"
>
  点击
</button>

<input 
  type="text"
  className="focus:outline-none focus:ring-2 focus:ring-amber-500"
/>
```

---

## 🎯 常见问题 FAQ

### Q1: 为什么不能使用 emoji？
- emoji 在不同系统上显示不一致
- 无法自定义颜色和大小
- 屏幕阅读器会读出 emoji 名称，影响体验
- 无法添加适当的 ARIA 属性

### Q2: 为什么 text-slate-500 不能用？
- `text-slate-500` 在深色背景上对比度不足 3:1
- WCAG AA 标准要求正文文本对比度至少 4.5:1
- 视力障碍用户难以阅读

### Q3: 如何选择合适的对比度？
- 正文文本：使用 `text-slate-300`（对比度~7.5:1）
- 次要文本：使用 `text-slate-400`（对比度~4.5:1）
- 装饰文本：使用 `text-slate-500`（但不可作为主要信息载体）

### Q4: 所有图标都要加 aria-hidden 吗？
- 装饰性图标：必须加 `aria-hidden="true"`
- 功能图标：添加 `aria-label="功能描述"` 或配合文字使用
- 状态图标：使用 `role="img"` + `aria-label`

---

## 📊 检查工具对比

| 工具 | 优点 | 缺点 | 推荐场景 |
|------|------|------|----------|
| PowerShell 脚本 | 快速、跨平台 | 功能简单 | 日常开发 |
| Git Hook | 自动执行、强制检查 | 需要配置 | 提交前检查 |
| CI/CD | 团队统一、记录历史 | 反馈慢 | 代码审查 |
| 浏览器插件 | 可视化、实时 | 手动操作 | 深度检查 |

---

## 🔗 相关资源

- [WCAG 2.1 对比度标准](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)
- [WebAIM 对比度检查器](https://webaim.org/resources/contrastchecker/)
- [axe-core 自动化测试](https://github.com/dequelabs/axe-core)
- [Lighthouse 无障碍审计](https://developer.chrome.com/docs/lighthouse/overview/)

---

**最后更新**: 2026-03-04  
**维护者**: Frontend Team
