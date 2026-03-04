import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { botApi, type Bot } from '../../lib/api'
import { useAuthStore } from '../../stores/authStore'

function RobotCard({ bot, onDelete }: { bot: Bot; onDelete: (id: string) => void }) {
  const navigate = useNavigate()
  const statusColors = {
    online: 'bg-green-500',
    offline: 'bg-gray-500',
    unknown: 'bg-yellow-500',
  }

  return (
    <div className="bg-slate-800 border border-slate-700 rounded-xl p-5">
      <div className="flex items-start justify-between">
        <div
          onClick={() => navigate(`/robots/${bot.id}`)}
          className="flex items-start gap-4 cursor-pointer flex-1"
        >
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
        <div className="flex gap-2 ml-4">
          <button
            onClick={() => navigate(`/robots/my/edit/${bot.id}`)}
            className="px-3 py-1.5 text-sm text-slate-400 hover:text-white border border-slate-600
                       hover:border-slate-400 rounded-lg transition"
          >
            编辑
          </button>
          <button
            onClick={() => onDelete(bot.id)}
            className="px-3 py-1.5 text-sm text-red-400 hover:text-red-300 border border-red-900
                       hover:border-red-700 rounded-lg transition"
          >
            删除
          </button>
        </div>
      </div>
    </div>
  )
}

export default function MyRobotsPage() {
  const navigate = useNavigate()
  const user = useAuthStore((s) => s.user)
  const [bots, setBots] = useState<Bot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadBots()
  }, [])

  const loadBots = async () => {
    try {
      const res = await botApi.list()
      const myBots = res.data.results.filter(
        (bot) => bot.master === user?.username || bot.master === user?.id
      )
      setBots(myBots)
    } catch (e: any) {
      setError(e.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要删除这个机器人吗？')) return
    try {
      await botApi.delete(id)
      setBots(bots.filter((b) => b.id !== id))
    } catch (e: any) {
      alert(e.response?.data?.detail || '删除失败')
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
            <span className="text-2xl">🤖</span>
            <span className="text-lg font-bold text-amber-400">我的机器人</span>
          </div>
          <button
            onClick={() => navigate('/robots/my/new')}
            className="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-lg
                       transition"
          >
            + 添加机器人
          </button>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-8">
        {error && (
          <div className="mb-4 p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
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
            <div className="text-5xl mb-4">🤖</div>
            <p className="text-slate-400 mb-4">你还没有登记机器人</p>
            <button
              onClick={() => navigate('/robots/my/new')}
              className="px-6 py-2 bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-lg
                         transition"
            >
              添加第一个机器人
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {bots.map((bot) => (
              <RobotCard key={bot.id} bot={bot} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </main>
    </div>
  )
}
