import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { botApi } from '../../lib/api'

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
    <div className="min-h-screen bg-slate-900">
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 h-16 flex items-center">
          <button onClick={() => navigate('/robots/my')} className="text-slate-400 hover:text-white">
            ← 返回
          </button>
          <span className="ml-4 text-lg font-bold text-amber-400">绑定机器人</span>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
              {error}
            </div>
          )}

          {success && (
            <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-xl text-green-400">
              {success}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              机器人QQ号 *
            </label>
            <input
              type="text"
              value={form.bot_id}
              onChange={(e) => setForm({ ...form, bot_id: e.target.value })}
              required
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2
                         text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              placeholder="输入要绑定的机器人QQ号"
            />
            <p className="mt-2 text-sm text-slate-500">
              输入机器人运行后通过注册 API 登记的 QQ 号，即可将其绑定到你的账号。
            </p>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={() => navigate('/robots/my')}
              className="flex-1 px-6 py-3 border border-slate-700 text-slate-300 font-medium rounded-lg
                         hover:border-slate-500 transition"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 px-6 py-3 bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-lg
                         transition disabled:opacity-50"
            >
              {submitting ? '绑定中...' : '绑定'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
