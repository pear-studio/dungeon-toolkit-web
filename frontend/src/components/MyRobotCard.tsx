import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot as BotIcon, RefreshCw, Trash2, Eye, EyeOff, Circle } from 'lucide-react'
import { type Bot } from '../lib/api'
import { TEXT, CARD, BUTTON, STATUS_COLORS, STATUS_TEXTS } from '../lib/constants'
import { cn } from '../lib/utils'

interface MyRobotCardProps {
  bot: Bot
  onDelete: (id: string) => void
  onRegenerateKey: (id: string) => void
}

/**
 * 我的机器人卡片组件 - 带 API Key 管理功能
 */
export default function MyRobotCard({ bot, onDelete, onRegenerateKey }: MyRobotCardProps) {
  const navigate = useNavigate()
  const [showKey, setShowKey] = useState(false)

  return (
    <div className={cn(CARD.base, "p-4")}>
      <div className="flex items-start justify-between">
        <button
          onClick={() => navigate(`/robots/${bot.id}`)}
          aria-label={`查看机器人 ${bot.nickname} 详情`}
          className="flex items-start gap-4 flex-1 text-left focus:outline-none focus:ring-2 focus:ring-blue-600 rounded-lg p-2 -m-2"
        >
          <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <BotIcon className="w-6 h-6 text-gray-600" aria-hidden="true" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className={cn(TEXT.h3, "truncate")}>{bot.nickname}</h3>
              <Circle className={cn("w-2 h-2 fill-current", STATUS_COLORS[bot.status])} aria-hidden="true" />
              <span className={TEXT.caption}>{STATUS_TEXTS[bot.status]}</span>
            </div>
            <p className={TEXT.bodySmall}>QQ: {bot.bot_id}</p>
            {bot.description && (
              <p className={cn(TEXT.bodySmall, "mt-1 line-clamp-2")}>{bot.description}</p>
            )}
          </div>
        </button>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1">
            <p className={cn(TEXT.caption, "mb-1")}>API Key</p>
            <div className="flex items-center gap-2">
              <code className="text-sm text-blue-600 bg-gray-50 px-2 py-1 rounded flex-1 truncate border border-gray-200">
                {showKey ? bot.api_key : '••••••••••••••••••••••••••••••••'}
              </code>
              <button
                onClick={() => setShowKey(!showKey)}
                className={cn(BUTTON.base, BUTTON.ghost, "px-2 py-1")}
                aria-label={showKey ? '隐藏 API Key' : '显示 API Key'}
              >
                {showKey ? <EyeOff className="w-4 h-4" aria-hidden="true" /> : <Eye className="w-4 h-4" aria-hidden="true" />}
              </button>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onRegenerateKey(bot.id)}
              className={cn(BUTTON.base, BUTTON.outline, BUTTON.sm)}
            >
              <RefreshCw className="w-4 h-4 inline mr-1" aria-hidden="true" />
              刷新
            </button>
            <button
              onClick={() => onDelete(bot.id)}
              className={cn(BUTTON.base, BUTTON.sm, "text-red-600 hover:text-red-700 border border-red-200 hover:border-red-300 focus:ring-red-500")}
            >
              <Trash2 className="w-4 h-4 inline mr-1" aria-hidden="true" />
              解绑
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}