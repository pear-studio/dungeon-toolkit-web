import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

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
      navigate('/dashboard')
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
          <h1 className="text-2xl font-bold text-gray-900">Dungeon Toolkit</h1>
          <p className="text-gray-600 mt-2">登录账户</p>
        </div>

        <div className="border border-gray-200 rounded-lg p-6">
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                邮箱 / 用户名
              </label>
              <input
                type="text"
                value={identifier}
                onChange={(e) => setIdentifier(e.target.value)}
                required
                placeholder="your@email.com 或 用户名"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900
                           placeholder-gray-400 focus:outline-none focus:border-blue-600 focus:ring-1
                           focus:ring-blue-600"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="至少 8 位"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-gray-900
                           placeholder-gray-400 focus:outline-none focus:border-blue-600 focus:ring-1
                           focus:ring-blue-600"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300
                         text-white font-medium rounded-lg transition
                         disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              {loading ? '登录中...' : '登录'}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-gray-600">
            还没有账户？{' '}
            <Link to="/register" className="text-blue-600 hover:text-blue-700 font-medium">
              立即注册
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}