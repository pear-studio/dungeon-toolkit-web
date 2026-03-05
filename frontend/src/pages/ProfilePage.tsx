import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { User, Bot as BotIcon, LogOut } from 'lucide-react'
import { botApi, type Bot } from '../lib/api'
import { TEXT, BUTTON, CARD, INPUT, ALERT, LAYOUT } from '../lib/constants'
import { cn } from '../lib/utils'
import Header from '../components/Header'
import MyRobotCard from '../components/MyRobotCard'
import RobotCardSkeleton from '../components/RobotCardSkeleton'
import EmptyState from '../components/EmptyState'

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

  const handleBindBot = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!bindBotId.trim()) return

    setBinding(true)
    try {
      await botApi.bind(bindBotId)
      setBindBotId('')
      await loadBots()
    } catch (e: unknown) {
      const err = e as { response?: { data?: { detail?: string; message?: string } } }
      alert(err.response?.data?.detail || err.response?.data?.message || '绑定失败')
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

      <main className={cn(LAYOUT.container, LAYOUT.section)}>
        <div className="mb-8">
          <h1 className={cn(TEXT.h1, "mb-2")}>个人中心</h1>
          <p className={TEXT.body}>管理您的账号信息和绑定的机器人</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 用户信息卡片 */}
          <div className="lg:col-span-1">
            <div className={CARD.base}>
              <div className="flex items-center gap-4 mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center">
                  <User className="w-8 h-8 text-blue-600" aria-hidden="true" />
                </div>
                <div>
                  <h2 className={TEXT.h3}>{user.username}</h2>
                  <p className={TEXT.bodySmall}>{user.email}</p>
                </div>
              </div>

              <button
                onClick={handleLogout}
                className={cn(BUTTON.base, BUTTON.danger, BUTTON.md, "w-full")}
              >
                <LogOut className="w-4 h-4" aria-hidden="true" />
                退出登录
              </button>
            </div>
          </div>

          {/* 机器人管理区域 */}
          <div className="lg:col-span-2">
            {/* 绑定新机器人 */}
            <div className={cn(CARD.base, "mb-6")}>
              <h2 className={cn(TEXT.h3, "mb-4")}>绑定新机器人</h2>
              <form onSubmit={handleBindBot} className="flex gap-4">
                <input
                  type="text"
                  value={bindBotId}
                  onChange={(e) => setBindBotId(e.target.value)}
                  placeholder="输入机器人 QQ 号"
                  className={cn(INPUT.base, "flex-1")}
                />
                <button
                  type="submit"
                  disabled={binding || !bindBotId.trim()}
                  className={cn(BUTTON.base, BUTTON.primary, BUTTON.md)}
                >
                  {binding ? '绑定中...' : '绑定'}
                </button>
              </form>
            </div>

            {/* 我的机器人列表 */}
            <div className={CARD.base}>
              <div className="flex items-center justify-between mb-4">
                <h2 className={TEXT.h3}>我的机器人</h2>
                <span className={TEXT.bodySmall}>{bots.length} 个</span>
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
                  icon={<BotIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" aria-hidden="true" />}
                  title="你还没有绑定机器人"
                  description="在上方输入机器人 QQ 号进行绑定"
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
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}