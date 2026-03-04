import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { LogOut, Bot, Settings, Castle, User } from 'lucide-react'

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-white">
      <nav className="border-b border-gray-200 bg-white sticky top-0 z-10">
        <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Settings className="w-8 h-8 text-gray-700" aria-hidden="true" />
            <span className="text-lg font-bold text-gray-900">Dungeon Toolkit</span>
          </div>
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-600 hidden sm:block flex items-center gap-1">
              <User className="w-4 h-4" aria-hidden="true" />
              {user?.username}
            </span>
            <button
              onClick={handleLogout}
              className="text-sm text-gray-700 hover:text-gray-900 transition px-3 py-1.5
                         border border-gray-300 hover:border-gray-400 rounded-lg
                         focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <LogOut className="w-4 h-4 inline mr-1" aria-hidden="true" />
              退出
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-6xl mx-auto px-4 py-10">
        <div className="mb-10 border border-gray-200 rounded-lg p-6">
          <div className="flex items-center gap-4">
            <Castle className="w-10 h-10 text-gray-700" aria-hidden="true" />
            <div>
              <h1 className="text-xl font-bold text-gray-900">
                欢迎回来，{user?.username}
              </h1>
              <p className="text-gray-600 mt-1">
                选择一个功能开始使用。
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button
            onClick={() => navigate('/robots')}
            className="p-6 border border-gray-200 rounded-lg
                       hover:border-blue-600 hover:bg-blue-50 transition text-left
                       focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <div className="flex items-start gap-4">
              <Bot className="w-8 h-8 text-gray-700" aria-hidden="true" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">机器人广场</h3>
                <p className="text-gray-600 text-sm">
                  浏览和管理 DicePP 机器人
                </p>
              </div>
            </div>
          </button>

          <button
            onClick={() => navigate('/robots/my')}
            className="p-6 border border-gray-200 rounded-lg
                       hover:border-blue-600 hover:bg-blue-50 transition text-left
                       focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            <div className="flex items-start gap-4">
              <Settings className="w-8 h-8 text-gray-700" aria-hidden="true" />
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-1">我的机器人</h3>
                <p className="text-gray-600 text-sm">
                  登记和管理我部署的机器人
                </p>
              </div>
            </div>
          </button>
        </div>
      </main>

      <footer className="border-t border-gray-200 mt-16 py-6 text-center text-sm text-gray-600">
        Dungeon Toolkit v0.1.0 · 使用 React + Django 构建
      </footer>
    </div>
  )
}
