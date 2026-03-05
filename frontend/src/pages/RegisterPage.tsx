import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { TEXT, BUTTON, CARD, INPUT, ALERT, LINK } from '../lib/constants'
import { cn } from '../lib/utils'

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
      navigate('/robots')
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
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-md px-4 py-8">
        <div className="text-center mb-8">
          <h1 className={TEXT.h1}>Dungeon Toolkit</h1>
          <p className={cn(TEXT.body, "mt-2")}>创建账户</p>
        </div>

        <div className={CARD.base}>
          {error && (
            <div className={cn(ALERT.error, "mb-4 text-sm")}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className={cn(TEXT.label, "mb-1")}>
                邮箱
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="your@email.com"
                className={cn(INPUT.base, "w-full")}
              />
            </div>

            <div>
              <label className={cn(TEXT.label, "mb-1")}>
                用户名
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                required
                placeholder="请输入用户名"
                minLength={2}
                maxLength={50}
                className={cn(INPUT.base, "w-full")}
              />
            </div>

            <div>
              <label className={cn(TEXT.label, "mb-1")}>
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="至少 8 位"
                className={cn(INPUT.base, "w-full")}
              />
            </div>

            <div>
              <label className={cn(TEXT.label, "mb-1")}>
                确认密码
              </label>
              <input
                type="password"
                value={confirm}
                onChange={(e) => setConfirm(e.target.value)}
                required
                placeholder="再次输入密码"
                className={cn(INPUT.base, "w-full")}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className={cn(BUTTON.base, BUTTON.primary, BUTTON.md, "w-full")}
            >
              {loading ? '注册中...' : '注册'}
            </button>
          </form>

          <p className={cn(TEXT.bodySmall, "mt-6 text-center")}>
            已有账户？{' '}
            <Link to="/login" className={LINK.primary}>
              立即登录
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}