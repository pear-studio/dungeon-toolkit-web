---
alwaysApply: false
description: 编写前端代码
---
# 前端开发规范

## 技术栈
- React 19 + TypeScript
- Vite 7 / Tailwind CSS 4
- Zustand (状态) / Axios (请求)

## 项目结构
```
frontend/src/
├── pages/        # 页面组件
├── components/   # 复用组件
├── stores/       # Zustand store
├── lib/          # 工具和常量
│   ├── api.ts
│   ├── constants.ts  # Design Tokens
│   └── utils.ts      # cn() 工具
└── index.css
```

## 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 组件 | PascalCase.tsx | `RobotCard.tsx` |
| 页面 | PascalCase + Page | `ProfilePage.tsx` |
| Store | camelCase + Store | `authStore.ts` |
| 工具 | camelCase.ts | `utils.ts`, `api.ts` |
| 常量 | UPPER_SNAKE | `TEXT`, `BUTTON`, `CARD` |

## Import 顺序
```tsx
// 1. React/外部库
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
// 2. 图标
import { User, LogOut } from 'lucide-react'
// 3. 内部工具
import { TEXT, BUTTON } from '../lib/constants'
import { cn } from '../lib/utils'
// 4. 组件
import Header from '../components/Header'
```

## 核心工具函数
```typescript
// lib/utils.ts
cn(...inputs: ClassValue[]): string  // clsx + tailwind-merge

// lib/api.ts
authApi.login(data: LoginData): Promise<AuthResponse>
authApi.register(data: RegisterData): Promise<AuthResponse>
authApi.me(): Promise<UserInfo>
botApi.list(params?): Promise<{results: Bot[]}>
botApi.listMy(): Promise<{results: Bot[]}>
botApi.get(id: string): Promise<Bot>
botApi.bind(botId: string): Promise<{message: string}>
botApi.regenerateKey(id: string): Promise<{api_key: string}>
botApi.delete(id: string): Promise<void>
```

## Design Tokens (lib/constants.ts)
```typescript
// 文字
TEXT.h1 | TEXT.h2 | TEXT.h3 | TEXT.body | TEXT.bodySmall | TEXT.label

// 按钮: base + variant + size
cn(BUTTON.base, BUTTON.primary, BUTTON.md)
// Variants: primary | secondary | danger | ghost | outline
// Sizes: sm | md | lg

// 卡片
CARD.base | CARD.compact | CARD.interactive | CARD.elevated

// 输入框
INPUT.base | INPUT.error

// 布局
LAYOUT.container | LAYOUT.section | LAYOUT.stack | LAYOUT.grid2 | LAYOUT.grid3

// 状态
STATUS_COLORS.online | STATUS_COLORS.offline | STATUS_COLORS.unknown
STATUS_TEXTS.online → '在线' | STATUS_TEXTS.offline → '离线'

// 提示
ALERT.info | ALERT.success | ALERT.warning | ALERT.error

// 链接
LINK.primary | LINK.secondary | LINK.nav
```

## 全局状态
```typescript
import { useAuthStore } from '../stores/authStore'
const user = useAuthStore((s) => s.user)
const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
const login = useAuthStore((s) => s.login)
const logout = useAuthStore((s) => s.logout)
const restoreSession = useAuthStore((s) => s.restoreSession)

// Token 存储
localStorage.getItem('access_token')
localStorage.getItem('refresh_token')
```

## 性能与请求约定

- 搜索输入默认使用防抖（建议 300-400ms），避免每个按键都发请求。
- 列表查询需处理竞态：只渲染最新一次请求的结果（latest-response-wins）。
- 路由页面优先使用懒加载（`React.lazy` + `Suspense`）并保持统一 fallback。
- 鉴权 401 默认走 refresh-first 策略，refresh 失败再执行登出退化流程。
- 生产环境禁止输出调试级 `console.log`。

## 错误处理
```tsx
try {
  await someApi()
  setError('')
} catch (e: unknown) {
  const err = e as { response?: { data?: { detail?: string } } }
  setError(err.response?.data?.detail || '操作失败')
}
```

## 组件模板
```tsx
import { useState } from 'react'
import { TEXT, BUTTON, CARD } from '../lib/constants'
import { cn } from '../lib/utils'

interface Props {
  // 类型定义
}

export default function ComponentName({ prop1 }: Props) {
  const [state, setState] = useState()

  return (
    <div className={CARD.base}>
      <h2 className={TEXT.h2}>标题</h2>
      <button className={cn(BUTTON.base, BUTTON.primary, BUTTON.md)}>
        操作
      </button>
    </div>
  )
}
```

## 关键规则
### 必须
- 使用 Design Tokens（`lib/constants.ts`）
- 使用 `cn()` 合并类名
- 使用 `lucide-react` 图标

### 禁止
- 硬编码 Tailwind 类
- 滥用 emoji（保持专业）
- 跳过错误处理

## 详细规范
完整代码示例见 `frontend/rules.md`