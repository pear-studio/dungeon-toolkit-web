import { useNavigate } from 'react-router-dom'
import { Bot as BotIcon, Circle } from 'lucide-react'
import { type Bot } from '../lib/api'
import { TEXT, CARD, STATUS_COLORS, STATUS_TEXTS } from '../lib/constants'
import { cn } from '../lib/utils'

interface RobotCardProps {
  bot: Bot
}

/**
 * 机器人卡片组件 - 用于广场列表展示
 */
export default function RobotCard({ bot }: RobotCardProps) {
  const navigate = useNavigate()

  return (
    <button
      onClick={() => navigate(`/robots/${bot.id}`)}
      aria-label={`查看机器人 ${bot.nickname} 详情`}
      className={cn(
        CARD.interactive,
        "w-full p-4 text-left",
        "focus:ring-2 focus:ring-gray-400"
      )}
    >
      <div className="flex items-start gap-4">
        {/* 头像 */}
        <div className={cn(
          "w-12 h-12 rounded-lg",
          "bg-gray-100",
          "flex items-center justify-center"
        )}>
          <BotIcon className="w-6 h-6 text-gray-600" aria-hidden="true" />
        </div>

        {/* 信息区域 */}
        <div className="flex-1 min-w-0">
          {/* 标题行 */}
          <div className="flex items-center gap-2">
            <h3 className={cn(TEXT.h3, "truncate")}>{bot.nickname}</h3>
            <Circle 
              className={cn("w-2 h-2 fill-current", STATUS_COLORS[bot.status])} 
              aria-hidden="true" 
            />
            <span className={TEXT.caption}>{STATUS_TEXTS[bot.status]}</span>
          </div>

          {/* QQ号 */}
          <p className={TEXT.bodySmall}>QQ: {bot.bot_id}</p>

          {/* 描述（可选） */}
          {bot.description && (
            <p className={cn(TEXT.bodySmall, "mt-1 line-clamp-2")}>{bot.description}</p>
          )}
        </div>
      </div>
    </button>
  )
}