import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Plus } from 'lucide-react'
import { botApi, type Bot } from '../../lib/api'
import { TEXT, BUTTON, ALERT, LAYOUT } from '../../lib/constants'
import { cn } from '../../lib/utils'
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

      <main className={cn(LAYOUT.container, LAYOUT.section)}>
        <div className="flex items-center justify-between mb-6">
          <h1 className={TEXT.h1}>我的机器人</h1>
          <button
            onClick={() => navigate('/profile')}
            className={cn(BUTTON.base, BUTTON.primary, BUTTON.md)}
          >
            <Plus className="w-4 h-4 inline mr-1" aria-hidden="true" />
            绑定机器人
          </button>
        </div>

        {error && (
          <div className={cn(ALERT.error, "mb-4")} role="alert">
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
                onClick={() => navigate('/profile')}
                className={cn(BUTTON.base, BUTTON.primary, BUTTON.md)}
              >
                绑定机器人
              </button>
            }
          />
        ) : (
          <div className={LAYOUT.stack}>
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