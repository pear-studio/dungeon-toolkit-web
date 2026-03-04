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
    online: 'text-green-600',
    offline: 'text-gray-400',
    unknown: 'text-yellow-600',
  }
  const statusTexts = {
    online: '在线',
    offline: '离线',
    unknown: '未知',
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-white flex items-center justify-center">
        <div className="text-gray-600">加载中...</div>
      </div>
    )
  }

  if (error || !bot) {
    return (
      <div className="min-h-screen bg-white">
        <nav className="border-b border-gray-200 bg-white sticky top-0 z-10">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center">
            <button onClick={() => navigate('/robots')} className="text-gray-700 hover:text-gray-900">
              ← 返回
            </button>
          </div>
        </nav>
        <div className="max-w-6xl mx-auto px-4 py-8 text-center text-red-600">
          {error || '机器人不存在'}
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center">
          <button 
            onClick={() => navigate('/robots')} 
            className="text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-600 rounded-lg p-2"
            aria-label="返回机器人广场"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <span className="ml-4 text-lg font-bold text-gray-900">机器人详情</span>
        </div>
      </nav>

      <main className="max-w-4xl mx-auto px-4 py-8">
        <div className="border border-gray-200 rounded-lg p-6">
          <div className="flex items-start gap-6">
            <div className="w-20 h-20 bg-gray-100 rounded-lg flex items-center justify-center">
              <BotIcon className="w-10 h-10 text-gray-600" aria-hidden="true" />
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-3 mb-2">
                <h1 className="text-xl font-bold text-gray-900">{bot.nickname}</h1>
                <span className={`font-medium ${statusColors[bot.status]} flex items-center gap-1 text-sm`}>
                  <Circle className="w-2 h-2 fill-current" aria-hidden="true" />
                  {statusTexts[bot.status]}
                </span>
              </div>
              <p className="text-gray-600 mb-4">QQ: {bot.bot_id}</p>
              {bot.description && (
                <p className="text-gray-600 mb-4">{bot.description}</p>
              )}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4 mt-6 pt-6 border-t border-gray-200">
            <div>
              <p className="text-gray-500 text-sm">版本</p>
              <p className="text-gray-900">{bot.version || '-'}</p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">主人</p>
              <p className="text-gray-900">QQ: {bot.master_qq}</p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">最后在线</p>
              <p className="text-gray-900">
                {bot.last_seen ? new Date(bot.last_seen).toLocaleString('zh-CN') : '-'}
              </p>
            </div>
            <div>
              <p className="text-gray-500 text-sm">添加时间</p>
              <p className="text-gray-900">{new Date(bot.created_at).toLocaleDateString('zh-CN')}</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
