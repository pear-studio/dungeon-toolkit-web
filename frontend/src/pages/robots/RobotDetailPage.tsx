import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { Bot as BotIcon, Circle } from 'lucide-react'
import { botApi, type Bot } from '../../lib/api'
import { TEXT, CARD, LAYOUT, STATUS_COLORS, STATUS_TEXTS } from '../../lib/constants'
import { cn } from '../../lib/utils'
import Header from '../../components/Header'

export default function RobotDetailPage() {
  const { id } = useParams<{ id: string }>()
  const [bot, setBot] = useState<Bot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (id) loadBot()
  }, [id])

  const loadBot = async () => {
    try {
      const res = await botApi.get(id!)
      setBot(res.data)
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      setError(err.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <p className={TEXT.body}>加载中...</p>
      </div>
    )
  }

  if (error || !bot) {
    return (
      <div className="min-h-screen bg-white">
        <Header />
        <div className={cn(LAYOUT.container, LAYOUT.section, "text-center")}>
          <p className={TEXT.error}>{error || '机器人不存在'}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className={cn(CARD.base, "p-6")}>
          <div className="flex items-start gap-6">
            <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center">
              <BotIcon className="w-10 h-10 text-gray-600" aria-hidden="true" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className={TEXT.h2}>{bot.nickname}</h1>
                <span className={cn("flex items-center gap-1 text-sm font-medium", STATUS_COLORS[bot.status])}>
                  <Circle className="w-2 h-2 fill-current" aria-hidden="true" />
                  {STATUS_TEXTS[bot.status]}
                </span>
              </div>
              <p className={cn(TEXT.bodySmall, "mb-4")}>QQ: {bot.bot_id}</p>
              {bot.description && (
                <p className={cn(TEXT.body, "mb-4")}>{bot.description}</p>
              )}
            </div>
          </div>

          <div className={cn(LAYOUT.grid2, "mt-6 pt-6 border-t border-gray-200")}>
            <div>
              <p className={TEXT.caption}>版本</p>
              <p className={TEXT.body}>{bot.version || '-'}</p>
            </div>
            <div>
              <p className={TEXT.caption}>主人</p>
              <p className={TEXT.body}>QQ: {bot.master_qq}</p>
            </div>
            <div>
              <p className={TEXT.caption}>最后在线</p>
              <p className={TEXT.body}>
                {bot.last_seen ? new Date(bot.last_seen).toLocaleString('zh-CN') : '-'}
              </p>
            </div>
            <div>
              <p className={TEXT.caption}>添加时间</p>
              <p className={TEXT.body}>{new Date(bot.created_at).toLocaleDateString('zh-CN')}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
