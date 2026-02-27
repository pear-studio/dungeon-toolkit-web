---
alwaysApply: false
description: 编写前端代码
---
# 前端开发规范

## 数据来源原则

### 禁止硬编码游戏内容数据

游戏内容数据（种族、职业、背景、法术等）**必须从后端 API 获取**，禁止写死在前端代码里。

```typescript
// 错误示例——硬编码种族名映射
const RACE_NAMES: Record<string, string> = {
  human: '人类', elf: '精灵', dwarf: '矮人',
}

// 错误示例——硬编码静态兜底数据
const BUILTIN_RACES = [
  { slug: 'human', name: '人类' },
  { slug: 'elf', name: '精灵' },
]
```

**原因**：静态数据会掩盖后端同步/导入错误，让问题在生产环境里悄无声息地失效。

### 正确做法：通过 `gamedataStore` 读取 API 数据

所有游戏内容数据都通过 `frontend/src/stores/gamedataStore.ts` 集中管理：

```typescript
import { useGamedataStore } from '../stores/gamedataStore'

function MyComponent() {
  const { races, classes, backgrounds, raceName, className } = useGamedataStore()

  // 获取显示名称（自动处理 custom__xxx slug）
  const name = raceName('human')          // → API 返回的名称，如 "人类"
  const cls  = className('fighter')       // → API 返回的名称，如 "战士"
}
```

在页面级组件的 `useEffect` 里调用 `fetchAll()` 来触发数据加载：

```typescript
const { fetchAll } = useGamedataStore()
useEffect(() => { fetchAll() }, [fetchAll])
```

`gamedataStore` 内部做了缓存（`loaded` flag），多次调用 `fetchAll()` 不会重复请求。

---

## 允许硬编码的内容

以下属于**规则常量**，不属于"游戏内容数据"，允许在前端代码中写死：

| 类型 | 示例 | 说明 |
|------|------|------|
| D&D 规则数值 | 标准数组 `[15, 14, 13, 12, 10, 8]`、点数购买规则 | PHB 中固定不变的规则数字 |
| UI 装饰映射 | `CLASS_ICONS`（职业 → emoji） | 纯展示用途，不影响业务逻辑 |
| 属性简写标签 | `STR / DEX / CON / INT / WIS / CHA` | 规则缩写，非内容数据 |
| 对齐阵营列表 | 守序善良、中立善良… | PHB 固定 9 阵营，极少变动 |

---

## 空状态处理

当 API 返回空数组时，**不要用静态数据兜底**，而应显示空状态提示，让问题暴露出来：

```tsx
// 正确：显示空状态
{races.length === 0 && (
  <p className="text-slate-500 text-sm">暂无可用种族，请检查后端数据导入</p>
)}

// 错误：用静态数据兜底掩盖问题
const displayRaces = races.length > 0 ? races : BUILTIN_RACES
```

---

## 组件结构规范

### 文件组织

```
frontend/src/
├── pages/          # 页面级组件（对应路由）
├── components/     # 通用复用组件
│   └── wizard/   # 角色创建向导子组件
├── stores/        # Zustand 状态管理
├── api/           # Axios 请求封装
└── types/         # TypeScript 类型定义
```

### 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| 页面组件 | PascalCase + `Page` 后缀 | `CharacterDetailPage.tsx` |
| 通用组件 | PascalCase | `RaceCard.tsx` |
| Store | camelCase + `Store` 后缀 | `gamedataStore.ts` |
| API 模块 | camelCase | `characters.ts` |

### 状态管理

- 全局持久状态 → Zustand store
- 表单/向导本地状态 → `useState` / `useReducer`
- 服务端缓存 → gamedataStore（带 `loaded` flag 防重复请求）
