import { useState, FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function RegisterPage() {
  const [email, setEmail] = useState('')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const register = useAuthStore((s) => s.register)
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    if (password !== confirm) {
      setError('两次输入的密码不一致')
      return
    }
    setLoading(true)
    try {
      await register(email, username, password)
      navigate('/dashboard')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: Record<string, string[]> } }
      const data = axiosErr.response?.data
      const msg = data
        ? Object.values(data).flat()[0]
        : '注册失败，请稍后重试'
      setError(msg || '注册失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900">
      {/* 背景装饰 */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-purple-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 left-1/4 w-80 h-80 bg-amber-500/5 rounded-full blur-3xl" />
      </div>

      <div className="relative w-full max-w-md px-4 py-8">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="text-5xl mb-3">⚔️</div>
          <h1 className="text-3xl font-bold text-amber-400">Dungeon Toolkit</h1>
          <p className="text-slate-400 mt-1">开始你的冒险之旅</p>
        </div>

        {/* 表单卡片 */}
        <div className="bg-slate-800 border border-slate-700 rounded-2xl p-8 shadow-2xl">
          <h2 className="text-xl font-semibold text-white mb-6">创建账户</h2>

          {error && (
            <div className="mb-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                邮箱
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="your@email.com"
                className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white
                           placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-1
                           focus:ring-amber-500 transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                冒险者名称（用户名）
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="你的专属名号"
                minLength={2}
                maxLength={50}
                className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white
                           placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-1
                           focus:ring-amber-500 transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="至少 8 位"
                className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white
                           placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-1
                           focus:ring-amber-500 transition"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-300 mb-1.5">
                确认密码
              </label>
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
                placeholder="再输一次"
                className="w-full px-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-white
                           placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-1
                           focus:ring-amber-500 transition"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-amber-500 hover:bg-amber-400 disabled:bg-amber-500/50
                         text-slate-900 font-semibold rounded-lg transition cursor-pointer
                         disabled:cursor-not-allowed"
            >
              {loading ? '注册中...' : '开始冒险'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-400">
            已有账户？{' '}
            <Link to="/login" className="text-amber-400 hover:text-amber-300 font-medium">
              直接登录
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
