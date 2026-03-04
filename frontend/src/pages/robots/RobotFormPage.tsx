import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { botApi } from '../../lib/api'

export default function RobotFormPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const isEdit = Boolean(id)

  const [loading, setLoading] = useState(isEdit)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState('')

  const [form, setForm] = useState({
    bot_id: '',
    nickname: '',
    master_qq: '',
    version: '',
    description: '',
    is_public: true,
  })

  useEffect(() => {
    if (isEdit && id) loadBot()
  }, [id])

  const loadBot = async () => {
    try {
      const res = await botApi.get(id!)
      const bot = res.data
      setForm({
        bot_id: bot.bot_id,
        nickname: bot.nickname,
        master_qq: bot.master_qq,
        version: bot.version || '',
        description: bot.description || '',
        is_public: bot.is_public,
      })
    } catch (e: any) {
      setError(e.response?.data?.detail || '加载失败')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    setError('')

    try {
      if (isEdit && id) {
        await botApi.update(id, form)
      } else {
        await botApi.create(form)
      }
      navigate('/robots/my')
    } catch (e: any) {
      setError(e.response?.data?.detail || e.response?.data?.message || '保存失败')
    } finally {
      setSubmitting(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 flex items-center justify-center">
        <div className="text-slate-400">加载中...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-2xl mx-auto px-4 h-16 flex items-center">
          <button onClick={() => navigate('/robots/my')} className="text-slate-400 hover:text-white">
            ← 返回
          </button>
          <span className="ml-4 text-lg font-bold text-amber-400">
            {isEdit ? '编辑机器人' : '添加机器人'}
          </span>
        </div>
      </nav>

      <main className="max-w-2xl mx-auto px-4 py-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className="p-4 bg-red-500/10 border border-red-500/30 rounded-xl text-red-400">
              {error}
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
              placeholder="机器人的QQ号"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              机器人昵称 *
            </label>
            <input
              type="text"
              value={form.nickname}
              onChange={(e) => setForm({ ...form, nickname: e.target.value })}
              required
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2
                         text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              placeholder="给机器人起个名字"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              你的QQ号 *
            </label>
            <input
              type="text"
              value={form.master_qq}
              onChange={(e) => setForm({ ...form, master_qq: e.target.value })}
              required
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2
                         text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              placeholder="你的QQ号"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              版本
            </label>
            <input
              type="text"
              value={form.version}
              onChange={(e) => setForm({ ...form, version: e.target.value })}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2
                         text-white placeholder-slate-500 focus:outline-none focus:border-amber-500"
              placeholder="如: v1.0.0"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              描述
            </label>
            <textarea
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
              rows={4}
              className="w-full bg-slate-800 border border-slate-700 rounded-lg px-4 py-2
                         text-white placeholder-slate-500 focus:outline-none focus:border-amber-500 resize-none"
              placeholder="介绍一下你的机器人有什么功能"
            />
          </div>

          <div className="flex items-center gap-3">
            <input
              type="checkbox"
              id="is_public"
              checked={form.is_public}
              onChange={(e) => setForm({ ...form, is_public: e.target.checked })}
              className="w-5 h-5 rounded border-slate-600 bg-slate-800 text-amber-500
                         focus:ring-amber-500 focus:ring-offset-0"
            />
            <label htmlFor="is_public" className="text-slate-300">
              公开显示在机器人广场
            </label>
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
              {submitting ? '保存中...' : '保存'}
            </button>
          </div>
        </form>
      </main>
    </div>
  )
}
