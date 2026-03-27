import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { TEXT, BUTTON, CARD, INPUT, ALERT, LINK } from '../lib/constants'
import { cn } from '../lib/utils'

export default function LoginPage() {
  const [identifier, setIdentifier] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const login = useAuthStore((s) => s.login)
  const navigate = useNavigate()

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(identifier, password)
      navigate('/robots')
    } catch (err: unknown) {
      const axiosErr = err as { response?: { data?: { non_field_errors?: string[]; detail?: string } } }
      const msg =
        axiosErr.response?.data?.non_field_errors?.[0] ||
        axiosErr.response?.data?.detail ||
        '登录失败，请检查账号和密码'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-white">
      <div className="w-full max-w-md px-4">
        <div className="text-center mb-8">
          <h1 className={TEXT.h1}>Dungeon Toolkit</h1>
          <p className={cn(TEXT.body, "mt-2")}>登录账户</p>
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
                邮箱 / 用户名
              </label>
              <input
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                required
                placeholder="your@email.com 或 用户名"
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

            <button
              type="submit"
              disabled={loading}
              className={cn(BUTTON.base, BUTTON.primary, BUTTON.md, "w-full")}
            >
              {loading ? '登录中...' : '登录'}
            </button>
          </form>

          <p className={cn(TEXT.bodySmall, "mt-6 text-center")}>
            还没有账户？{' '}
            <Link to="/register" className={LINK.primary}>
              立即注册
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}