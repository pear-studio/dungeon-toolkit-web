import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bot as BotIcon, Search, Filter, ArrowLeft, Circle } from 'lucide-react'
import { botApi, type Bot } from '../../lib/api'

function RobotCard({ bot }: { bot: Bot }) {
  const navigate = useNavigate()
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
    <button
      onClick={() => navigate(`/robots/${bot.id}`)}
      className="bg-slate-800 border border-slate-700 rounded-xl p-5 text-left
                 hover:border-amber-500/50 transition
                 focus:outline-none focus:ring-2 focus:ring-amber-500 focus:ring-offset-2 focus:ring-offset-slate-900"
    >
      <div className="flex items-start gap-4">
        <div className="w-14 h-14 bg-slate-700 rounded-xl flex items-center justify-center">
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
      </div>
    </button>
  )
}

export default function RobotPlazaPage() {
  const navigate = useNavigate()
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
            <span className="text-lg font-bold text-amber-400">机器人广场</span>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex gap-4 mb-6">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" aria-hidden="true" />
            <input
              type="text"
              placeholder="搜索机器人..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2
                         text-white placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500"
            />
          </div>
          <div className="relative">
            <Filter className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400" aria-hidden="true" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-8 py-2
                         text-white focus:outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500"
            >
              <option value="">全部状态</option>
              <option value="online">在线</option>
              <option value="offline">离线</option>
            </select>
          </div>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400" role="alert">
            {error}
          </div>
        )}

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {[1, 2, 3].map((i) => (
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
            <p className="text-slate-300">暂无机器人</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {bots.map((bot) => (
              <RobotCard key={bot.id} bot={bot} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
