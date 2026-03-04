import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { User, Bot as BotIcon, RefreshCw, Trash2, Eye, EyeOff, Circle, LogOut } from 'lucide-react'
import { botApi, type Bot } from '../lib/api'
import Header from '../components/Header'

function BoundBotCard({ bot, onDelete, onRegenerateKey }: { 
  bot: Bot; 
  onDelete: (id: string) => void;
  onRegenerateKey: (id: string) => void;
}) {
  const [showKey, setShowKey] = useState(false)

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

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex items-start justify-between">
        <button
          onClick={() => window.location.href = `/robots/${bot.id}`}
          className="flex items-start gap-4 flex-1 text-left focus:outline-none focus:ring-2 focus:ring-blue-600 rounded-lg p-2 -m-2"
        >
          <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0">
            <BotIcon className="w-6 h-6 text-gray-600" aria-hidden="true" />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <h3 className="font-medium text-gray-900 truncate">{bot.nickname}</h3>
              <Circle className={`w-2 h-2 fill-current ${statusColors[bot.status]}`} aria-hidden="true" />
              <span className="text-xs text-gray-500">{statusTexts[bot.status]}</span>
            </div>
            <p className="text-sm text-gray-600">QQ: {bot.bot_id}</p>
            {bot.description && (
              <p className="text-sm text-gray-600 mt-1 line-clamp-2">{bot.description}</p>
            )}
          </div>
        </button>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between gap-4">
          <div className="flex-1">
            <p className="text-xs text-gray-500 mb-1">API Key</p>
            <div className="flex items-center gap-2">
              <code className="text-sm text-blue-600 bg-gray-50 px-2 py-1 rounded flex-1 truncate border border-gray-200">
                {showKey ? bot.api_key : '••••••••••••••••••••••••••••••••'}
              </code>
              <button
                onClick={() => setShowKey(!showKey)}
                className="text-xs text-gray-700 hover:text-gray-900 px-2 focus:outline-none focus:ring-2 focus:ring-blue-600 rounded"
                aria-label={showKey ? '隐藏 API Key' : '显示 API Key'}
              >
                {showKey ? <EyeOff className="w-4 h-4" aria-hidden="true" /> : <Eye className="w-4 h-4" aria-hidden="true" />}
              </button>
            </div>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => onRegenerateKey(bot.id)}
              className="px-3 py-1.5 text-sm text-gray-700 hover:text-gray-900 border border-gray-300
                         hover:border-gray-400 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <RefreshCw className="w-4 h-4 inline mr-1" aria-hidden="true" />
              刷新
            </button>
            <button
              onClick={() => onDelete(bot.id)}
              className="px-3 py-1.5 text-sm text-red-600 hover:text-red-700 border border-red-200
                         hover:border-red-300 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-red-500"
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

export default function ProfilePage() {
  const navigate = useNavigate()
  const { user, logout } = useAuthStore()
  const [bots, setBots] = useState<Bot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [bindBotId, setBindBotId] = useState('')
  const [binding, setBinding] = useState(false)

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

  const handleBindBot = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!bindBotId.trim()) return

    setBinding(true)
    try {
      await botApi.bind(bindBotId)
      setBindBotId('')
      await loadBots()
    } catch (e: any) {
      alert(e.response?.data?.detail || e.response?.data?.message || '绑定失败')
    } finally {
      setBinding(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/robots')
  }

  if (!user) {
    return null
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">个人中心</h1>
          <p className="text-gray-600">管理您的账号信息和绑定的机器人</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <div className="border border-gray-200 rounded-lg p-6">
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-8 h-8 text-blue-600" aria-hidden="true" />
                </div>
                <div>
                  <h2 className="text-lg font-semibold text-gray-900">{user.username}</h2>
                  <p className="text-sm text-gray-600">{user.email}</p>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="w-full flex items-center justify-center gap-2 px-4 py-2 text-red-600 border border-red-200
                           hover:bg-red-50 rounded-lg transition focus:outline-none focus:ring-2 focus:ring-red-500"
              >
                <LogOut className="w-4 h-4" aria-hidden="true" />
                退出登录
              </button>
            </div>
          </div>

          <div className="lg:col-span-2">
            <div className="border border-gray-200 rounded-lg p-6 mb-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">绑定新机器人</h2>
              <form onSubmit={handleBindBot} className="flex gap-4">
                <input
                  type="text"
                  value={bindBotId}
                  onChange={(e) => setBindBotId(e.target.value)}
                  placeholder="输入机器人 QQ 号"
                  className="flex-1 border border-gray-300 rounded-lg px-4 py-2
                             text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
                />
                <button
                  type="submit"
                  disabled={binding || !bindBotId.trim()}
                  className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg
                             transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-600"
                >
                  {binding ? '绑定中...' : '绑定'}
                </button>
              </form>
            </div>

            <div className="border border-gray-200 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">我的机器人</h2>
                <span className="text-sm text-gray-600">{bots.length} 个</span>
              </div>

              {error && (
                <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700" role="alert">
                  {error}
                </div>
              )}

              {loading ? (
                <div className="space-y-4">
                  {[1, 2].map((i) => (
                    <div key={i} className="border border-gray-200 rounded-lg p-4 animate-pulse">
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 bg-gray-100 rounded-lg" />
                        <div className="flex-1 space-y-2">
                          <div className="h-4 bg-gray-100 rounded w-2/3" />
                          <div className="h-3 bg-gray-100 rounded w-1/2" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : bots.length === 0 ? (
                <div className="text-center py-12">
                  <BotIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" aria-hidden="true" />
                  <p className="text-gray-600">你还没有绑定机器人</p>
                  <p className="text-sm text-gray-500 mt-2">
                    在上方输入机器人 QQ 号进行绑定
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {bots.map((bot) => (
                    <BoundBotCard 
                      key={bot.id} 
                      bot={bot} 
                      onDelete={handleDelete}
                      onRegenerateKey={handleRegenerateKey}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
