# DNDChar 前端设计规范

> 本文件记录项目统一的 UI 设计 Token，所有前端组件必须遵循此规范。
> 最后更新：2026-02-26

---

## 1. 颜色体系（Color Tokens）

### 背景色

| 用途 | Tailwind 类 | 说明 |
|------|------------|------|
| 页面底色 | `bg-slate-900` | 最深层，整个页面背景 |
| 卡片 / 面板 | `bg-slate-800` | 主要容器、侧边栏、弹窗 |
| 内嵌控件 | `bg-slate-700` | 输入框、下拉、小按钮内部 |
| 半透明遮罩 | `bg-slate-800/60` | 折叠区域、次级面板 |
| 选中高亮 | `bg-amber-500/10` | 已选中的卡片/按钮背景 |

> ⚠️ **重要**：所有 `<button>` 卡片的背景必须加 `!` 前缀（如 `!bg-slate-800`），
> 防止浏览器默认样式覆盖自定义背景色，导致白底白字问题。

### 文字色

| 用途 | Tailwind 类 | 说明 |
|------|------------|------|
| 页面级大标题 | `text-slate-100` | 最亮，用于 H1 |
| 普通正文 / 卡片选项名称 | `text-slate-200` | 未选中时的卡片文字，禁止使用 `text-white` |
| 标签 / 区块小标题 | `text-slate-300` | section 内的 h2/h3 |
| 次要说明 / 描述 | `text-slate-400` | 副标题、提示、描述文字 |
| 占位 / 禁用 / 注释 | `text-slate-500` | placeholder、灰色备注 |
| 强调 / 选中 | `text-amber-400` | 选中状态的文字 |
| 输入框内文字 | `text-white` | 仅在确定背景为 `bg-slate-700/800` 时使用 |

> ⚠️ **禁止**：在任何浅色背景（`bg-white`、`bg-slate-100/200/300`）上使用 `text-white`。

### 边框色

| 用途 | Tailwind 类 |
|------|------------|
| 默认卡片边框 | `border-slate-700` |
| 输入框边框 | `border-slate-600` |
| 悬停边框 | `border-slate-600` / `border-slate-500` |
| 选中边框 | `border-amber-500` |
| 选中边框（弱） | `border-amber-500/60` |
| 强调面板边框 | `border-amber-500/20` |

### 功能色

| 用途 | Tailwind 类 |
|------|------------|
| 主操作按钮 | `bg-amber-500 text-slate-900` |
| 主操作按钮 hover | `hover:bg-amber-400` |
| 成功 / 正向修正值 | `text-green-400` |
| 危险 / 负向修正值 | `text-red-400` |
| 必填标记 | `text-red-400`（`*`） |
| 施法标记 | `text-purple-400` |
| 种族加成 | `text-blue-400` |

---

## 2. 字体规范（Typography）

| 层级 | 类 | 用途 |
|------|-----|------|
| 页面标题 | `text-2xl font-bold` | Dashboard H1 |
| 区块标题 | `text-base font-semibold` | Wizard section 标题 |
| 卡片主文字 | `text-sm font-medium` | 选项名、标签 |
| 说明文字 | `text-xs` | 描述、注释、提示 |
| 数值大字 | `text-lg font-bold` | 属性值、骰点结果 |
| 数值中字 | `text-base font-bold` | 汇总数值 |

---

## 3. 圆角规范（Border Radius）

| 用途 | 类 |
|------|-----|
| 大卡片 / 面板 | `rounded-xl` |
| 小按钮 / 标签 | `rounded-lg` |
| 超小标签 / 徽章 | `rounded-full` / `rounded` |

---

## 4. 间距规范（Spacing）

| 用途 | 类 |
|------|-----|
| 卡片内边距（标准） | `p-3` |
| 卡片内边距（宽松） | `p-4` / `p-5` |
| 输入框内边距 | `px-3 py-2` / `px-4 py-3` |
| 区块间距 | `space-y-4` / `space-y-6` |
| 网格间距 | `gap-2` |

---

## 5. 交互规范（Interaction States）

### 卡片选择按钮模板

```tsx
<button
  className={`p-3 rounded-xl border-2 text-left transition
    ${selected
      ? 'border-amber-500 !bg-amber-500/10'       // 选中态
      : 'border-slate-700 !bg-slate-800 hover:border-slate-600'  // 默认态
    }`}
>
  <div className={`text-sm font-medium ${selected ? 'text-amber-400' : 'text-slate-200'}`}>
    选项名称
  </div>
  <div className="text-xs text-slate-500 mt-0.5">说明文字</div>
</button>
```

> `!bg-` 是必须的，防止浏览器对 `<button>` 注入默认背景。

### 输入框模板

```tsx
<input
  className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg
             text-white text-sm placeholder-slate-500
             focus:outline-none focus:border-amber-500 transition"
/>
```

### 禁用状态

```tsx
disabled:opacity-30 disabled:cursor-not-allowed
```

---

## 6. 禁止事项（Anti-patterns）

| ❌ 禁止 | ✅ 替代 |
|---------|--------|
| `text-white` 在浅/中性背景上 | `text-slate-200` |
| `bg-white` 或 `bg-slate-100/200` | `bg-slate-800` 或 `bg-slate-700` |
| `<button>` 卡片不加 `!bg-` | 必须加 `!bg-slate-800` |
| 卡片 `border-2` 不写背景色 | 始终配对 `border + bg` |
| emoji 作为功能性图标 | 纯文字或 SVG 图标 |
| 本地 `useEffect` 单独 fetch 数据 | 统一通过 `gamedataStore` 获取 |
