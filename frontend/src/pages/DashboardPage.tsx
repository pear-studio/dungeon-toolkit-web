import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-slate-900">
      <nav className="border-b border-slate-800 bg-slate-900/80 backdrop-blur sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚔️</span>
            <span className="text-lg font-bold text-amber-400">Dungeon Toolkit</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-slate-400 hidden sm:block">
              🧙 {user?.username}
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-slate-400 hover:text-white transition px-3 py-1.5
                         border border-slate-700 hover:border-slate-500 rounded-lg"
            >
              退出
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-10">
        <div className="mb-10 bg-gradient-to-r from-amber-500/10 via-purple-500/10 to-slate-800
                        border border-amber-500/20 rounded-2xl p-8">
          <div className="flex items-center gap-4">
            <div className="text-5xl">🏰</div>
            <div>
              <h1 className="text-2xl font-bold text-white">
                欢迎回来，<span className="text-amber-400">{user?.username}</span>！
              </h1>
              <p className="text-slate-400 mt-1">
                选择一个功能开始使用。
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <button
            onClick={() => navigate('/robots')}
            className="p-6 bg-slate-800 border border-slate-700 rounded-xl
                       hover:border-amber-500/50 transition cursor-pointer text-left"
          >
            <div className="text-3xl mb-3">🎲</div>
            <h3 className="text-lg font-semibold text-white mb-2">机器人广场</h3>
            <p className="text-slate-400 text-sm">
              浏览和管理 DicePP 机器人
            </p>
          </button>

          <button
            onClick={() => navigate('/robots/my')}
            className="p-6 bg-slate-800 border border-slate-700 rounded-xl
                       hover:border-amber-500/50 transition cursor-pointer text-left"
          >
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="text-lg font-semibold text-white mb-2">我的机器人</h3>
            <p className="text-slate-400 text-sm">
              登记和管理我部署的机器人
            </p>
          </button>
        </div>
      </main>

      <footer className="border-t border-slate-800 mt-16 py-6 text-center text-sm text-slate-600">
        Dungeon Toolkit v0.1.0 · 使用 React + Django 构建
      </footer>
    </div>
  )
}
