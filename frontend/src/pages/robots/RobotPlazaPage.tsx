import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { botApi, type Bot } from '../../lib/api'

function RobotCard({ bot }: { bot: Bot }) {
  const navigate = useNavigate()
  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-gray-500',
    unknown: 'bg-yellow-500',
  }

  return (
    <div
      onClick={() => navigate(`/robots/${bot.id}`)}
      className="bg-slate-800 border border-slate-700 rounded-xl p-5 cursor-pointer
                 hover:border-amber-500/50 transition"
    >
      <div className="flex items-start gap-4">
        <div className="w-14 h-14 bg-slate-700 rounded-xl flex items-center justify-center text-2xl">
          🤖
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2">
            <h3 className="font-semibold text-white truncate">{bot.nickname}</h3>
            <span className={`w-2 h-2 rounded-full ${statusColors[bot.status]}`} />
          </div>
          <p className="text-sm text-slate-400">QQ: {bot.bot_id}</p>
          {bot.description && (
            <p className="text-sm text-slate-500 mt-1 line-clamp-2">{bot.description}</p>
          )}
        </div>
      </div>
    </div>
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
            <button onClick={() => navigate('/dashboard')} className="text-slate-400 hover:text-white">
              ←
            </button>
            <span className="text-2xl">🎲</span>
            <span className="text-lg font-bold text-amber-400">机器人广场</span>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex gap-4 mb-6">
          <input
            type="text"
            placeholder="搜索机器人..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-slate-800 border border-slate-700 rounded-lg px-4 py-2
                       text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
          />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded-lg px-4 py-2
                       text-white focus:outline-none focus:border-amber-500"
          >
            <option value="">全部状态</option>
            <option value="online">在线</option>
            <option value="offline">离线</option>
          </select>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
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
            <div className="text-5xl mb-4">🤖</div>
            <p className="text-slate-400">暂无机器人</p>
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
