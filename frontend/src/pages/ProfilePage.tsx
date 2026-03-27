import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { User, Bot as BotIcon, LogOut } from 'lucide-react'
import { botApi, type Bot } from '../lib/api'
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

      <main className="max-w-6xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">个人中心</h1>
          <p className="text-gray-600">管理您的账号信息和绑定的机器人</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 用户信息卡片 */}
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

          {/* 机器人管理区域 */}
          <div className="lg:col-span-2">
            {/* 绑定新机器人 */}
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

            {/* 我的机器人列表 */}
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
                <RobotCardSkeleton count={2} layout="list" />
              ) : bots.length === 0 ? (
                <EmptyState
                  icon={<BotIcon className="w-16 h-16 text-gray-300 mx-auto mb-4" aria-hidden="true" />}
                  title="你还没有绑定机器人"
                  description="在上方输入机器人 QQ 号进行绑定"
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
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}