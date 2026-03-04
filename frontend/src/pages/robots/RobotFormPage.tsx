import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, Bot } from 'lucide-react'
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
          <button 
            onClick={() => navigate('/robots/my')} 
            className="text-slate-300 hover:text-white focus:outline-none focus:ring-2 focus:ring-amber-500 rounded-lg p-2"
            aria-label="返回我的机器人"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <Bot className="w-8 h-8 text-amber-400 ml-4" aria-hidden="true" />
          <span className="ml-4 text-lg font-bold text-amber-400">绑定机器人</span>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400" role="alert">
              {error}
            </div>
          )}

          {success && (
            <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-xl text-green-400" role="alert">
              {success}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              机器人 QQ 号 *
            </label>
            <input
              type="text"
              value={form.bot_id}
              onChange={(e) => setForm({ ...form, bot_id: e.target.value })}
              required
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2
                         text-white placeholder-slate-400 focus:outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500"
              placeholder="输入要绑定的机器人 QQ 号"
            />
            <p className="mt-2 text-sm text-slate-400">
              输入机器人运行后通过注册 API 登记的 QQ 号，即可将其绑定到你的账号。
            </p>
          </div>

          <div className="flex gap-4 pt-4">
            <button
              type="button"
              onClick={() => navigate('/robots/my')}
              className="flex-1 px-6 py-3 border border-slate-700 text-slate-300 font-medium rounded-lg
                         hover:border-slate-500 transition focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={submitting}
              className="flex-1 px-6 py-3 bg-amber-500 hover:bg-amber-600 text-white font-medium rounded-lg
                         transition disabled:opacity-50 focus:outline-none focus:ring-2 focus:ring-amber-500"
            >
              {submitting ? '绑定中...' : '绑定'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
