import { useNavigate } from 'react-router-dom'
import { Bot as BotIcon, Circle } from 'lucide-react'
import { type Bot } from '../lib/api'
import { BOT_STATUS_COLORS, BOT_STATUS_TEXTS } from '../lib/constants'

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
      className="border border-gray-300 rounded-lg p-4 text-left bg-gray-50
                 hover:border-gray-400 hover:bg-gray-100 transition
                 focus:outline-none focus:ring-2 focus:ring-gray-400"
    >
      <div className="flex items-start gap-4">
        <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
          <BotIcon className="w-6 h-6 text-gray-600" aria-hidden="true" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-medium text-gray-900 truncate">{bot.nickname}</h3>
            <Circle className={`w-2 h-2 fill-current ${BOT_STATUS_COLORS[bot.status]}`} aria-hidden="true" />
            <span className="text-xs text-gray-500">{BOT_STATUS_TEXTS[bot.status]}</span>
          </div>
          <p className="text-sm text-gray-600">QQ: {bot.bot_id}</p>
          {bot.description && (
            <p className="text-sm text-gray-600 mt-1 line-clamp-2">{bot.description}</p>
          )}
        </div>
      </div>
    </button>
  )
}