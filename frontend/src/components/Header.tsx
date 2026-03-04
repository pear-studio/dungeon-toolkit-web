import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Bot as BotIcon, LogIn, User, LogOut } from 'lucide-react'

export default function Header() {
  const navigate = useNavigate()
  const { isAuthenticated, user, logout } = useAuthStore()

  const handleLogout = () => {
    logout()
    navigate('/robots')
  }

  return (
    <nav className="border-b border-gray-200 bg-white sticky top-0 z-10">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={() => navigate('/robots')}
            className="text-gray-700 hover:text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-600 rounded-lg p-2"
            aria-label="返回机器人广场"
          >
            <BotIcon className="w-8 h-8" aria-hidden="true" />
          </button>
          <span className="text-lg font-bold text-gray-900">Dungeon Toolkit</span>
        </div>

        <div className="flex items-center gap-2">
          {isAuthenticated ? (
            <>
              <button
                onClick={() => navigate('/profile')}
                className="flex items-center gap-2 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg
                           focus:outline-none focus:ring-2 focus:ring-blue-600"
                aria-label="个人中心"
              >
                <User className="w-5 h-5" aria-hidden="true" />
                <span className="hidden sm:inline text-sm">{user?.username || '个人中心'}</span>
              </button>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg
                           focus:outline-none focus:ring-2 focus:ring-red-600"
                aria-label="退出登录"
              >
                <LogOut className="w-5 h-5" aria-hidden="true" />
                <span className="hidden sm:inline text-sm">退出</span>
              </button>
            </>
          ) : (
            <button
              onClick={() => navigate('/login')}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg
                         hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-600"
              aria-label="登录"
            >
              <LogIn className="w-5 h-5" aria-hidden="true" />
              <span className="hidden sm:inline text-sm">登录</span>
            </button>
          )}
        </div>
      </div>
    </nav>
  )
}
