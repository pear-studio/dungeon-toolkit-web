import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { Bot as BotIcon, ArrowLeft, Circle } from 'lucide-react'
import { botApi, type Bot } from '../../lib/api'

export default function RobotDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
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
    } catch (e: any) {
      setError(e.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const statusColors = {
    online: 'text-green-400',
    offline: 'text-gray-400',
    unknown: 'text-yellow-400',
  }
  const statusTexts = {
    online: '在线',
    offline: '离线',
    unknown: '未知',
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-300">加载中...</div>
      </div>
    )
  }

  if (error || !bot) {
    return (
      <div className="min-h-screen bg-slate-900">
        <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center">
            <button onClick={() => navigate('/robots')} className="text-slate-400 hover:text-white">
              ← 返回
            </button>
          </div>
        </nav>
        <div className="max-w-6xl mx-auto px-4 py-8 text-center text-red-400">
          {error || '机器人不存在'}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center">
          <button 
            onClick={() => navigate('/robots')} 
            className="text-slate-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-amber-500 rounded-lg p-2"
            aria-label="返回机器人广场"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <span className="ml-4 text-lg font-bold text-amber-400">机器人详情</span>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-slate-800 border border-slate-700 rounded-xl p-6">
          <div className="flex items-start gap-6">
            <div className="w-24 h-24 bg-slate-700 rounded-xl flex items-center justify-center">
              <BotIcon className="w-12 h-12 text-slate-300" aria-hidden="true" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-2xl font-bold text-white">{bot.nickname}</h1>
                <span className={`font-semibold ${statusColors[bot.status]} flex items-center gap-1`}>
                  <Circle className="w-2 h-2 fill-current" aria-hidden="true" />
                  {statusTexts[bot.status]}
                </span>
              </div>
              <p className="text-slate-300 mb-4">QQ: {bot.bot_id}</p>
              {bot.description && (
                <p className="text-slate-300 mb-4">{bot.description}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-slate-700">
            <div>
              <p className="text-slate-400 text-sm">版本</p>
              <p className="text-white">{bot.version || '-'}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">主人</p>
              <p className="text-white">QQ: {bot.master_qq}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">最后在线</p>
              <p className="text-white">
                {bot.last_seen ? new Date(bot.last_seen).toLocaleString('zh-CN') : '-'}
              </p>
            </div>
            <div>
              <p className="text-slate-400 text-sm">添加时间</p>
              <p className="text-white">{new Date(bot.created_at).toLocaleDateString('zh-CN')}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
