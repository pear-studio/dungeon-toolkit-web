# 前端开发规范

## 项目架构

```
src/
├── components/    # 可复用 UI 组件（无业务逻辑）
├── pages/         # 页面组件（对应路由）
├── stores/        # 全局状态管理 (Zustand)
├── lib/           # 工具函数和常量
│   ├── api.ts        # API 请求封装
│   ├── constants.ts  # Design Tokens（样式常量）
│   └── utils.ts      # 工具函数（如 cn）
└── index.css      # 全局样式（仅 Tailwind 导入和 base 层重置）
```

## Design Token 系统

### 核心原则

1. **所有样式通过 `constants.ts` 集中管理**
2. **组件内不写硬编码的 Tailwind 类**（除非是一次性的布局类如 `flex`、`mb-4`）
3. **使用 `cn()` 工具函数合并类名**

### 可用 Token

| Token | 用途 | 示例 |
|-------|------|------|
| `TEXT` | 文字样式 | `TEXT.h1`, `TEXT.bodySmall`, `TEXT.label` |
| `BUTTON` | 按钮样式 | `cn(BUTTON.base, BUTTON.primary, BUTTON.md)` |
| `CARD` | 卡片容器 | `CARD.base`, `CARD.compact`, `CARD.interactive` |
| `INPUT` | 输入框 | `INPUT.base`, `INPUT.error` |
| `ALERT` | 提示框 | `ALERT.error`, `ALERT.success` |
| `LAYOUT` | 布局 | `LAYOUT.container`, `LAYOUT.grid3`, `LAYOUT.stack` |
| `LINK` | 链接 | `LINK.primary`, `LINK.nav` |
| `STATUS_COLORS` | 状态颜色 | `STATUS_COLORS.online` |

### 按钮组合方式

```tsx
// 基础 + 变体 + 尺寸
<button className={cn(BUTTON.base, BUTTON.primary, BUTTON.md)}>
  提交
</button>

// 添加额外样式
<button className={cn(BUTTON.base, BUTTON.danger, BUTTON.md, "w-full")}>
  删除
</button>
```

## cn() 工具函数

`cn()` = `clsx` + `tailwind-merge`

- 合并多个类名
- 处理条件类名
- 自动解决 Tailwind 冲突（后者覆盖前者）

```tsx
import { cn } from '../lib/utils'

// 基础用法
cn('text-red-500', 'text-blue-500')  // → 'text-blue-500'（后者覆盖）

// 条件类名
cn(TEXT.body, isActive && 'font-bold')

// 合并 Token 和额外样式
cn(CARD.base, "mb-6")
```

## 组件开发规范

### 1. 文件命名
- 组件：`PascalCase.tsx`（如 `RobotCard.tsx`）
- 工具：`camelCase.ts`（如 `utils.ts`）

### 2. 组件结构
```tsx
import { ... } from 'react'
import { TEXT, BUTTON } from '../lib/constants'
import { cn } from '../lib/utils'

interface Props {
  // 定义 Props 类型
}

export default function ComponentName({ prop1, prop2 }: Props) {
  // 状态和逻辑

  return (
    // JSX
  )
}
```

### 3. 可访问性 (a11y)
- 图标添加 `aria-hidden="true"`
- 按钮/链接有明确文字或 `aria-label`
- 错误信息添加 `role="alert"`
- 表单控件关联 `label`

### 4. UI 风格
- **不滥用 emoji**：仅在必要时使用，保持界面简洁专业
- 优先使用 `lucide-react` 图标库

## 常见错误

### ❌ 忘记内边距
```tsx
// 错误：提取常量时丢失 padding
base: 'border border-gray-200 rounded-lg bg-white'

// 正确：卡片必须包含内边距
base: 'border border-gray-200 rounded-lg bg-white p-6'
```

### ❌ 重复定义样式
```tsx
// 错误：每个组件单独写
<p className="text-sm text-gray-600">...</p>

// 正确：使用 Token
<p className={TEXT.bodySmall}>...</p>
```

### ❌ 硬编码状态样式
```tsx
// 错误
{status === 'online' ? 'text-green-600' : 'text-gray-400'}

// 正确
STATUS_COLORS[status]
```

## 新增样式的流程

1. 先检查 `constants.ts` 是否已有合适的 Token
2. 如果没有，在 `constants.ts` 中添加新 Token
3. 在组件中通过 `cn()` 使用 Token
4. 考虑是否需要多种变体（如尺寸、颜色）

## 依赖说明

| 包 | 用途 |
|----|------|
| `react` | UI 框架 |
| `react-router-dom` | 路由 |
| `zustand` | 状态管理 |
| `axios` | HTTP 请求 |
| `lucide-react` | 图标库 |
| `clsx` | 条件类名 |
| `tailwind-merge` | Tailwind 类合并 |
| `tailwindcss` | CSS 框架 |
