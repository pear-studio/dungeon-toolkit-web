import { useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot as BotIcon, Circle, MessageCircle } from 'lucide-react'
import { type Bot } from '../lib/api'
import { BUTTON, TEXT, CARD, STATUS_COLORS, STATUS_TEXTS } from '../lib/constants'
import { cn } from '../lib/utils'

interface RobotCardProps {
  bot: Bot
  onOpenChat?: (bot: Bot) => void
}

/**
 * 机器人卡片组件 - 用于广场列表展示
 */
export default function RobotCard({ bot, onOpenChat }: RobotCardProps) {
  const navigate = useNavigate()
  const canOpenChat = bot.status === 'online'

  const handleNavigate = useCallback(() => {
    navigate(`/robots/${bot.id}`)
  }, [navigate, bot.id])

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' || e.key === ' ') {
      navigate(`/robots/${bot.id}`)
    }
  }, [navigate, bot.id])

  return (
    <div
      onClick={handleNavigate}
      onKeyDown={handleKeyDown}
      role="button"
      tabIndex={0}
      aria-label={`查看机器人 ${bot.nickname} 详情`}
      className={cn(
        CARD.interactive,
        "w-full p-4 text-left",
        "focus:ring-2 focus:ring-gray-400"
      )}
    >
      <div className="flex items-start gap-4">
        <div className={cn(
          "w-12 h-12 rounded-lg",
          "bg-gray-100",
          "flex items-center justify-center"
        )}>
          <BotIcon className="w-6 h-6 text-gray-600" aria-hidden="true" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className={cn(TEXT.h3, "truncate")}>{bot.nickname}</h3>
            <Circle
              className={cn("w-2 h-2 fill-current", STATUS_COLORS[bot.status])}
              aria-hidden="true"
            />
            <span className={TEXT.caption}>{STATUS_TEXTS[bot.status]}</span>
          </div>

          <p className={TEXT.bodySmall}>QQ: {bot.bot_id}</p>

          {bot.description && (
            <p className={cn(TEXT.bodySmall, "mt-1 line-clamp-2")}>{bot.description}</p>
          )}

          {onOpenChat && canOpenChat && (
            <button
              type="button"
              onClick={(e) => {
                e.preventDefault()
                e.stopPropagation()
                onOpenChat(bot)
              }}
              className={cn(BUTTON.base, BUTTON.outline, BUTTON.sm, 'mt-2')}
            >
              <MessageCircle className="w-4 h-4 inline mr-1" aria-hidden="true" />
              打开聊天
            </button>
          )}
        </div>
      </div>
    </div>
  )
}