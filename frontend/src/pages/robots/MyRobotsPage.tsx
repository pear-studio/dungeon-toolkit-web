import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { botApi, type Bot } from '../../lib/api'
import Header from '../../components/Header'
import MyRobotCard from '../../components/MyRobotCard'
import RobotCardSkeleton from '../../components/RobotCardSkeleton'
import EmptyState from '../../components/EmptyState'

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
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      setError(err.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm('确定要解绑这个机器人吗？')) return
    try {
      await botApi.delete(id)
      setBots(bots.filter((b) => b.id !== id))
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      alert(err.response?.data?.detail || '解绑失败')
    }
  }

  const handleRegenerateKey = async (id: string) => {
    if (!confirm('确定要刷新 API Key 吗？刷新后旧 Key 将失效。')) return
    try {
      const res = await botApi.regenerateKey(id)
      setBots(bots.map(b => b.id === id ? { ...b, api_key: res.data.api_key } : b))
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string } } }
      alert(err.response?.data?.detail || '刷新失败')
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-2xl font-bold text-gray-900">我的机器人</h1>
          <button
            onClick={() => navigate('/robots/my/bind')}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg
                       transition focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <Plus className="w-4 h-4 inline mr-1" aria-hidden="true" />
            绑定机器人
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700" role="alert">
            {error}
          </div>
        )}

        {loading ? (
          <RobotCardSkeleton count={2} layout="list" />
        ) : bots.length === 0 ? (
          <EmptyState
            title="你还没有绑定机器人"
            description="机器人通过注册 API 登记后，你可以在这里绑定管理"
            action={
              <button
                onClick={() => navigate('/robots/my/bind')}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg
                           transition focus:outline-none focus:ring-2 focus:ring-blue-600"
              >
                绑定第一个机器人
              </button>
            }
          />
        ) : (
          <div className="space-y-4">
            {bots.map((bot) => (
              <MyRobotCard
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