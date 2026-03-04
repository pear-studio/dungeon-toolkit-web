import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot as BotIcon, Plus, RefreshCw, Trash2, Eye, EyeOff, Circle, ArrowLeft } from 'lucide-react'
import { botApi, type Bot } from '../../lib/api'

function RobotCard({ bot, onDelete, onRegenerateKey }: { 
  bot: Bot; 
  onDelete: (id: string) => void;
  onRegenerateKey: (id: string) => void;
}) {
  const navigate = useNavigate()
  const [showKey, setShowKey] = useState(false)

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

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
      <div className="flex items-start justify-between">
        <button
          onClick={() => navigate(`/robots/${bot.id}`)}
          className="flex items-start gap-4 flex-1 text-left focus:outline-none focus:ring-2 focus:ring-amber-500 rounded-lg p-2 -m-2"
        >
          <div className="w-14 h-14 bg-slate-700 rounded-xl flex items-center justify-center flex-shrink-0">
            <BotIcon className="w-8 h-8 text-slate-300" aria-hidden="true" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-white truncate">{bot.nickname}</h3>
              <Circle className={`w-2 h-2 fill-current ${statusColors[bot.status]}`} aria-hidden="true" />
              <span className="sr-only">{statusTexts[bot.status]}</span>
            </div>
            <p className="text-sm text-slate-300">QQ: {bot.bot_id}</p>
            {bot.description && (
              <p className="text-sm text-slate-300 mt-1 line-clamp-2">{bot.description}</p>
            )}
          </div>
        </button>
      </div>

      <div className="mt-4 pt-4 border-t border-slate-700">
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1">
            <p className="text-xs text-slate-400 mb-1">API Key</p>
            <div className="flex items-center gap-2">
              <code className="text-sm text-amber-400 bg-slate-900 px-2 py-1 rounded flex-1 truncate">
                {showKey ? bot.api_key : '••••••••••••••••••••••••••••••••'}
              </code>
              <button
                onClick={() => setShowKey(!showKey)}
                className="text-xs text-slate-300 hover:text-white px-2 focus:outline-none focus:ring-2 focus:ring-amber-500 rounded"
                aria-label={showKey ? '隐藏 API Key' : '显示 API Key'}
              >
                {showKey ? <EyeOff className="w-4 h-4" aria-hidden="true" /> : <Eye className="w-4 h-4" aria-hidden="true" />}
              </button>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onRegenerateKey(bot.id)}
              className="px-3 py-1.5 text-sm text-slate-300 hover:text-white border border-slate-600
                         hover:border-slate-400 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              <RefreshCw className="w-4 h-4 inline mr-1" aria-hidden="true" />
              刷新
            </button>
            <button
              onClick={() => onDelete(bot.id)}
              className="px-3 py-1.5 text-sm text-red-400 hover:text-red-300 border border-red-900
                         hover:border-red-700 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-red-500"
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

export default function MyRobotsPage() {
  const navigate = useNavigate()
  const [bots, setBots] = useState<Bot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadBots()
  }, [])

  const loadBots = async () => {
    try {
      const res = await botApi.listMy()
      setBots(res.data.results || res.data)
    } catch (e: any) {
      setError(e.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要解绑这个机器人吗？')) return
    try {
      await botApi.delete(id)
      setBots(bots.filter((b) => b.id !== id))
    } catch (e: any) {
      alert(e.response?.data?.detail || '解绑失败')
    }
  }

  const handleRegenerateKey = async (id: string) => {
    if (!confirm('确定要刷新 API Key 吗？刷新后旧 Key 将失效。')) return
    try {
      const res = await botApi.regenerateKey(id)
      setBots(bots.map(b => b.id === id ? { ...b, api_key: res.data.api_key } : b))
    } catch (e: any) {
      alert(e.response?.data?.detail || '刷新失败')
    }
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button 
              onClick={() => navigate('/dashboard')} 
              className="text-slate-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-amber-500 rounded-lg p-2"
              aria-label="返回仪表盘"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <BotIcon className="w-8 h-8 text-amber-400" aria-hidden="true" />
            <span className="text-lg font-bold text-amber-400">我的机器人</span>
          </div>
          <button
            onClick={() => navigate('/robots/my/bind')}
            className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-lg
                       transition focus:outline-none focus:ring-2 focus:ring-amber-500"
          >
            <Plus className="w-4 h-4 inline mr-1" aria-hidden="true" />
            绑定机器人
          </button>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400" role="alert">
            {error}
          </div>
        )}

        {loading ? (
          <div className="space-y-4">
            {[1, 2].map((i) => (
              <div key={i} className="bg-slate-800 border border-slate-700 rounded-xl p-5 animate-pulse">
                <div className="flex items-start gap-4">
                  <div className="w-14 h-14 bg-slate-700 rounded-xl" />
                  <div className="flex-1 space-y-2">
                    <div className="h-4 bg-slate-700 rounded w-2/3" />
                    <div className="h-3 bg-slate-700 rounded w-1/2" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : bots.length === 0 ? (
          <div className="text-center py-20">
            <BotIcon className="w-16 h-16 text-slate-500 mx-auto mb-4" aria-hidden="true" />
            <p className="text-slate-300 mb-4">你还没有绑定机器人</p>
            <p className="text-sm text-slate-400 mb-6">
              机器人通过注册 API 登记后，你可以在这里绑定管理
            </p>
            <button
              onClick={() => navigate('/robots/my/bind')}
              className="px-6 py-2 bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-lg
                         transition focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              绑定第一个机器人
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {bots.map((bot) => (
              <RobotCard 
                key={bot.id} 
                bot={bot} 
                onDelete={handleDelete}
                onRegenerateKey={handleRegenerateKey}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
