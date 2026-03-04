import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Bot as BotIcon, Search, Filter, Circle, Castle } from 'lucide-react'
import { botApi, type Bot } from '../lib/api'
import Header from '../components/Header'

function RobotCard({ bot }: { bot: Bot }) {
  const navigate = useNavigate()
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
            <Circle className={`w-2 h-2 fill-current ${statusColors[bot.status]}`} aria-hidden="true" />
            <span className="text-xs text-gray-500">{statusTexts[bot.status]}</span>
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

export default function DashboardPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [bots, setBots] = useState<Bot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [search, setSearch] = useState('')
  const [statusFilter, setStatusFilter] = useState('')

  useEffect(() => {
    loadBots()
  }, [search, statusFilter])

  const loadBots = async () => {
    setLoading(true)
    try {
      const params: { search?: string; status?: string } = {}
      if (search) params.search = search
      if (statusFilter) params.status = statusFilter
      const res = await botApi.list(params)
      setBots(res.data.results)
      setError('')
    } catch (e: any) {
      setError(e.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8 border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-4">
            <Castle className="w-10 h-10 text-gray-700" aria-hidden="true" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                {user ? `欢迎回来，${user.username}` : '欢迎使用 Dungeon Toolkit'}
              </h1>
              <p className="text-gray-600 mt-1">
                {user ? '浏览和管理 DicePP 机器人' : '登录以管理您的机器人'}
              </p>
            </div>
          </div>
        </div>

        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" aria-hidden="true" />
            <input
              type="text"
              placeholder="搜索机器人..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full border border-gray-300 rounded-lg pl-10 pr-4 py-2
                         text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" aria-hidden="true" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="border border-gray-300 rounded-lg pl-10 pr-8 py-2
                         text-gray-900 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
            >
              <option value="">全部状态</option>
              <option value="online">在线</option>
              <option value="offline">离线</option>
            </select>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700" role="alert">
            {error}
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
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
          <div className="text-center py-20">
            <BotIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" aria-hidden="true" />
            <p className="text-gray-600">暂无机器人</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {bots.map((bot) => (
              <RobotCard key={bot.id} bot={bot} />
            ))}
          </div>
        )}

        <div className="mt-10 text-center">
          <button
            onClick={() => navigate('/robots')}
            className="text-blue-600 hover:text-blue-700 text-sm"
          >
            查看更多机器人 →
          </button>
        </div>
      </main>

      <footer className="border-t border-gray-200 mt-16 py-6 text-center text-sm text-gray-600">
        Dungeon Toolkit v0.1.0 · 使用 React + Django 构建
      </footer>
    </div>
  )
}
