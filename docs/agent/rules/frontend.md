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

## Design Token 系统
- 样式通过 `lib/constants.ts` 集中管理
- 使用 `cn()` 合并类名
- 详见 `frontend/rules.md`

## 核心 Token
- TEXT: h1/h2/h3/body/bodySmall/label
- BUTTON: base + primary/secondary/danger + sm/md/lg
- CARD: base/compact/interactive
- INPUT/ALERT/LAYOUT/LINK

## 命名
- 组件: PascalCase (`RobotCard.tsx`)
- 工具: camelCase (`utils.ts`)
- Store: camelCase + Store (`authStore.ts`)

## 详细规范
完整代码示例和 Token 列表见 `frontend/rules.md`
