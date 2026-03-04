import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { botApi } from '../../lib/api'
import Header from '../../components/Header'

export default function RobotFormPage() {
  const navigate = useNavigate()

  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [form, setForm] = useState({
    bot_id: '',
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')
    setSuccess('')

    try {
      await botApi.bind(form.bot_id)
      setSuccess('绑定成功！')
      setTimeout(() => navigate('/robots/my'), 1500)
    } catch (e: any) {
      setError(e.response?.data?.detail || e.response?.data?.message || '绑定失败')
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen bg-white">
      <Header />

      <main className="max-w-2xl mx-auto px-4 py-8">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900">绑定机器人</h1>
        </div>
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="p-4 bg-green-50 border border-green-200 rounded-lg text-green-700" role="alert">
              {success}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              机器人 QQ 号 *
            </label>
            <input
              type="text"
              value={form.bot_id}
              onChange={(e) => setForm({ ...form, bot_id: e.target.value })}
              required
              className="w-full border border-gray-300 rounded-lg px-4 py-2
                         text-gray-900 placeholder-gray-400 focus:outline-none focus:border-blue-600 focus:ring-1 focus:ring-blue-600"
              placeholder="输入要绑定的机器人 QQ 号"
            />
            <p className="mt-2 text-sm text-gray-500">
              输入机器人运行后通过注册 API 登记的 QQ 号，即可将其绑定到你的账号。
            </p>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={() => navigate('/robots/my')}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 font-medium rounded-lg
                         hover:border-gray-400 transition focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg
                         transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              {submitting ? '绑定中...' : '绑定'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
