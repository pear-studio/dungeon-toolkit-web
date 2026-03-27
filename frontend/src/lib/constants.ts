/**
 * 机器人状态相关常量
 */
export const BOT_STATUS_COLORS = {
  online: 'text-green-600',
  offline: 'text-gray-400',
  unknown: 'text-yellow-600',
} as const

export const BOT_STATUS_TEXTS = {
  online: '在线',
  offline: '离线',
  unknown: '未知',
} as const

export type BotStatus = keyof typeof BOT_STATUS_COLORS