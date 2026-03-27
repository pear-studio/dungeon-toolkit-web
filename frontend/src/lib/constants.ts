 /**
 * 设计令牌系统 (Design Tokens)
 * 
 * 集中管理所有 UI 样式常量，确保设计一致性。
 * 修改此文件可以全局更新应用外观。
 */

// ============================================
// 文字样式 (Typography)
// ============================================

export const TEXT = {
  // 标题
  h1: 'text-2xl font-bold text-gray-900',
  h2: 'text-xl font-semibold text-gray-900',
  h3: 'text-lg font-medium text-gray-900',
  
  // 正文
  body: 'text-base text-gray-700',
  bodySmall: 'text-sm text-gray-600',
  
  // 辅助文字
  caption: 'text-xs text-gray-500',
  label: 'text-sm font-medium text-gray-700',
  
  // 特殊
  error: 'text-sm text-red-600',
  success: 'text-sm text-green-600',
} as const

// ============================================
// 按钮样式 (Buttons)
// ============================================

export const BUTTON = {
  // 基础样式（所有按钮共用）
  base: 'font-medium rounded-lg transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2',
  
  // 尺寸
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
  
  // 变体
  primary: 'bg-blue-600 hover:bg-blue-700 text-white focus:ring-blue-600',
  secondary: 'bg-gray-100 hover:bg-gray-200 text-gray-700 focus:ring-gray-400',
  danger: 'bg-red-600 hover:bg-red-700 text-white focus:ring-red-600',
  ghost: 'bg-transparent hover:bg-gray-100 text-gray-700 focus:ring-gray-400',
  outline: 'border border-gray-300 hover:border-gray-400 bg-transparent text-gray-700 focus:ring-gray-400',
} as const

// ============================================
// 卡片样式 (Cards)
// ============================================

export const CARD = {
  // 基础卡片（带内边距）
  base: 'border border-gray-200 rounded-lg bg-white p-6',
  
  // 紧凑卡片（小内边距）
  compact: 'border border-gray-200 rounded-lg bg-white p-4',
  
  // 可交互卡片（可点击）
  interactive: 'border border-gray-300 rounded-lg bg-gray-50 p-4 hover:bg-gray-100 hover:border-gray-400 transition-colors',
  
  // 带阴影的卡片
  elevated: 'border border-gray-200 rounded-lg bg-white p-6 shadow-sm',
} as const

// ============================================
// 输入框样式 (Inputs)
// ============================================

export const INPUT = {
  base: 'w-full border border-gray-300 rounded-lg px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600',
  error: 'w-full border border-red-300 rounded-lg px-4 py-2 text-gray-900 placeholder-gray-400 focus:outline-none focus:border-red-600 focus:ring-1 focus:ring-red-600',
} as const

// ============================================
// 状态颜色 (Status Colors)
// ============================================

export const STATUS_COLORS = {
  online: 'text-green-600',
  offline: 'text-gray-400',
  unknown: 'text-yellow-600',
} as const

export const STATUS_BG_COLORS = {
  online: 'bg-green-100 text-green-800',
  offline: 'bg-gray-100 text-gray-600',
  unknown: 'bg-yellow-100 text-yellow-800',
} as const

// ============================================
// 状态文字 (Status Labels)
// ============================================

export const STATUS_TEXTS = {
  online: '在线',
  offline: '离线',
  unknown: '未知',
} as const

// ============================================
// 布局常量 (Layout)
// ============================================

export const LAYOUT = {
  container: 'max-w-6xl mx-auto px-4',
  section: 'py-8',
  stack: 'space-y-4',
  grid2: 'grid grid-cols-1 md:grid-cols-2 gap-4',
  grid3: 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4',
} as const

// ============================================
// 反馈样式 (Feedback)
// ============================================

export const ALERT = {
  info: 'p-4 bg-blue-50 border border-blue-200 rounded-lg text-blue-700',
  success: 'p-4 bg-green-50 border border-green-200 rounded-lg text-green-700',
  warning: 'p-4 bg-yellow-50 border border-yellow-200 rounded-lg text-yellow-700',
  error: 'p-4 bg-red-50 border border-red-200 rounded-lg text-red-700',
} as const

// ============================================
// 链接样式 (Links)
// ============================================

export const LINK = {
  primary: 'text-blue-600 hover:text-blue-700 font-medium',
  secondary: 'text-gray-600 hover:text-gray-800',
  nav: 'text-gray-600 hover:text-gray-900 font-medium',
} as const

// ============================================
// 类型导出
// ============================================

export type BotStatus = keyof typeof STATUS_COLORS
